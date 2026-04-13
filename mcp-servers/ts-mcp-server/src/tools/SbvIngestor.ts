/**
 * SbvIngestor — Evidence-pipeline-compliant ingestor for SBV data.
 *
 * Pulls conversations + messages from the SBV REST API and routes them through
 * the exact same chain-of-custody pipeline as SmsEvidenceIngestor:
 *
 *   1. SHA-256 hash of the raw API response   ← FIRST TOUCH
 *   2. DuckDB dedup check (ingestion_log)      ← FINGERPRINT
 *   3. DuckDB logIngestion() + UUIDv7          ← REGISTER
 *   4. Normalize SbvMessage → NormalizedMessage
 *   5. PostgreSQL evidence.documents            ← STRUCTURED WRITE
 *   6. PostgreSQL evidence.conversations
 *   7. PostgreSQL evidence.messages (with content_hash per message)
 *   8. DuckDB updateWriteTracking()             ← AUDIT COMPLETE
 *
 * Evidence handling is always critical first — hashing and UIDs before
 * anything else, 100%.
 */

import { createHash } from 'crypto';
import { uuidv7 } from 'uuidv7';
import { DuckDbVault } from './DuckDbVault.js';
import { PostgresWriter } from './PostgresWriter.js';
import { SbvClient, SbvMessage, SbvCall, SbvConversation } from './SbvClient.js';
import { NormalizedMessage } from './SmsXmlParser.js';
import { CALL_TYPE_LABELS } from './constants.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SbvIngestOptions {
  deviceId?: string;
  caseId?: string;
}

interface ConversationBucket {
  id: string;
  participants: string[];
  messages: NormalizedMessage[];
  conversationHash: string;
}

export interface SbvIngestResult {
  status: 'ingested' | 'duplicate' | 'empty' | 'failed';
  ingestion_id?: string;
  source_hash?: string;
  document_id?: string;
  message_count?: number;
  conversation_count?: number;
  call_count?: number;
  error?: string;
}

// ---------------------------------------------------------------------------
// Ingestor
// ---------------------------------------------------------------------------

export class SbvIngestor {
  private readonly client: SbvClient;

  constructor(
    private readonly vault: DuckDbVault,
    private readonly pg: PostgresWriter,
    client?: SbvClient,
  ) {
    this.client = client ?? new SbvClient();
  }

  /**
   * Pull all conversations + messages + calls from SBV and ingest them
   * through the full evidence pipeline.
   */
  async ingest(options: SbvIngestOptions = {}): Promise<SbvIngestResult> {
    // -----------------------------------------------------------------
    // 1. Fetch raw data from SBV API
    // -----------------------------------------------------------------
    let conversations: SbvConversation[];
    let allMessages: SbvMessage[];
    let calls: SbvCall[];

    try {
      [conversations, allMessages, calls] = await Promise.all([
        this.client.getConversations(),
        this.client.getAllMessages(),
        this.client.getCalls(),
      ]);
    } catch (err: any) {
      return { status: 'failed', error: `SBV API unreachable: ${err.message}` };
    }

    if (allMessages.length === 0 && calls.length === 0) {
      return { status: 'empty', message_count: 0, call_count: 0 };
    }

    // -----------------------------------------------------------------
    // 2. SHA-256 hash at FIRST TOUCH — before any transformation
    // -----------------------------------------------------------------
    const rawPayload = JSON.stringify({ conversations, messages: allMessages, calls });
    const sourceHash = this.sha256(rawPayload);

    // -----------------------------------------------------------------
    // 3. DuckDB dedup check
    // -----------------------------------------------------------------
    const existing = await this.vault.getIngestionByHash(sourceHash);
    if (existing) {
      return {
        status: 'duplicate',
        ingestion_id: existing.id,
        source_hash: existing.source_hash,
      };
    }

    // -----------------------------------------------------------------
    // 4. DuckDB register — logIngestion() + UUIDv7
    // -----------------------------------------------------------------
    const ingestion = await this.vault.logIngestion(
      'sbv_api_pull',
      'sbv-full-export',
      rawPayload,
      null,
      {
        case_id: options.caseId ?? null,
        device_id: options.deviceId ?? null,
        source_platform: 'sbv',
        extraction_method: 'api_pull',
        conversation_count: conversations.length,
        message_count: allMessages.length,
        call_count: calls.length,
      },
    );

    // -----------------------------------------------------------------
    // 5. Normalize SBV messages → NormalizedMessage[]
    // -----------------------------------------------------------------
    const normalized = this.normalizeMessages(allMessages, calls);

    // -----------------------------------------------------------------
    // 6. PostgreSQL: evidence.documents
    // -----------------------------------------------------------------
    const documentId = uuidv7();
    await this.pg.writeRecord('evidence.documents', {
      id: documentId,
      filename: 'sbv-full-export.json',
      file_hash: sourceHash,
      file_size: Buffer.byteLength(rawPayload, 'utf8'),
      file_type: 'application/json',
      source_platform: 'sbv',
      acquisition_method: 'api_pull',
      acquisition_date: new Date().toISOString(),
      processing_status: 'parsed',
      message_count: normalized.length,
      metadata: {
        ingestion_id: ingestion.id,
        source_hash: sourceHash,
        sbv_conversation_count: conversations.length,
        sbv_call_count: calls.length,
      },
    });

    // -----------------------------------------------------------------
    // 7. Bucket into conversations → PostgreSQL writes
    // -----------------------------------------------------------------
    const buckets = this.bucketConversations(normalized);

    for (const conversation of buckets.values()) {
      const ordered = [...conversation.messages].sort((a, b) =>
        a.metadata.timestamp.localeCompare(b.metadata.timestamp),
      );
      const first = ordered[0];
      const last = ordered[ordered.length - 1];

      await this.pg.writeRecord('evidence.conversations', {
        id: conversation.id,
        platform: 'sms',
        participants: conversation.participants,
        message_count: conversation.messages.length,
        start_date: first?.metadata.timestamp ?? null,
        end_date: last?.metadata.timestamp ?? null,
        last_message: last?.text ?? '',
        metadata: {
          conversation_hash: conversation.conversationHash,
          source_hash: sourceHash,
          source_document_id: documentId,
          source_ingestion_id: ingestion.id,
          source: 'sbv',
        },
      });

      for (const record of ordered) {
        const rawData = JSON.parse(record.metadata.raw_data);
        const contentHash = this.sha256(
          JSON.stringify({
            raw_data: rawData,
            timestamp: record.metadata.timestamp,
            sender: record.metadata.sender,
            recipient: record.metadata.recipient,
            record_type: record.metadata.record_type,
          }),
        );

        await this.pg.writeRecord('evidence.messages', {
          id: uuidv7(),
          conversation_id: conversation.id,
          sender: record.metadata.sender || 'Unknown',
          recipient: record.metadata.recipient || null,
          body: record.text,
          timestamp: record.metadata.timestamp,
          platform: 'sms',
          direction: this.detectDirection(record),
          message_type: this.detectMessageType(record),
          content_hash: contentHash,
          device_id: options.deviceId ?? null,
          sender_normalized: this.normalizeParticipant(record.metadata.sender),
          recipient_normalized: this.normalizeParticipant(record.metadata.recipient),
          external_id: contentHash.slice(0, 16),
          raw_data: rawData,
          attachments: record.metadata.has_attachments
            ? { attachment_count: record.metadata.attachment_count, has_attachments: true }
            : null,
          provenance: {
            source_hash: sourceHash,
            conversation_hash: conversation.conversationHash,
            source_document_id: documentId,
            source_ingestion_id: ingestion.id,
            source: 'sbv',
            hash_levels: {
              source_hash: sourceHash,
              conversation_hash: conversation.conversationHash,
              content_hash: contentHash,
            },
            record_type: record.metadata.record_type,
            raw_address: record.metadata.raw_address,
            contact_name: record.metadata.contact_name,
            type_code: record.metadata.type_code,
            duration_seconds: record.metadata.duration_seconds,
            result_label: record.metadata.result_label,
          },
        });
      }
    }

    // -----------------------------------------------------------------
    // 8. DuckDB write tracking — audit trail complete
    // -----------------------------------------------------------------
    await this.vault.updateWriteTracking(ingestion.id, 'postgresql', true);

    return {
      status: 'ingested',
      ingestion_id: ingestion.id,
      source_hash: sourceHash,
      document_id: documentId,
      message_count: normalized.length,
      conversation_count: buckets.size,
      call_count: calls.length,
    };
  }

  // -----------------------------------------------------------------------
  // Normalization — SBV types → NormalizedMessage
  // -----------------------------------------------------------------------

  private normalizeMessages(messages: SbvMessage[], calls: SbvCall[]): NormalizedMessage[] {
    const results: NormalizedMessage[] = [];

    for (const msg of messages) {
      const timestamp = this.parseTimestamp(msg.date);
      const isSent = msg.type === 2;
      const contactLabel = msg.contact_name || msg.address || 'Unknown';

      const sender = isSent ? 'Me' : contactLabel;
      const recipient = isSent ? contactLabel : 'Me';
      const body = msg.body ?? '';
      if (!body.trim()) continue;

      const hasParts = Array.isArray(msg.parts) && msg.parts.length > 0;
      const attachmentParts = hasParts
        ? msg.parts!.filter((p) => p.content_type && !p.content_type.startsWith('text/'))
        : [];

      results.push({
        text: body.trim(),
        metadata: {
          timestamp,
          sender,
          recipient,
          raw_address: msg.address || '',
          contact_name: msg.contact_name || 'Unknown',
          record_type: (msg.ct_t || hasParts) ? 'mms' : 'message',
          raw_data: JSON.stringify(msg),
          type_code: String(msg.type),
          status_code: String(msg.status),
          read_status: String(msg.read),
          message_box: msg.msg_box !== undefined ? String(msg.msg_box) : undefined,
          has_attachments: attachmentParts.length > 0 ? true : undefined,
          attachment_count: attachmentParts.length > 0 ? attachmentParts.length : undefined,
        },
      });
    }

    // Calls → NormalizedMessage (same pattern as SmsXmlParser)
    for (const call of calls) {
      const timestamp = this.parseTimestamp(call.date);
      const contactLabel = call.contact_name || call.number || 'Unknown';
      const isOutgoing = call.type === 2;

      const sender = isOutgoing ? 'Me' : contactLabel;
      const recipient = isOutgoing ? contactLabel : 'Me';
      const label = CALL_TYPE_LABELS[String(call.type)] ?? 'Unknown';
      let text = `${label} Call with ${contactLabel} (Duration: ${call.duration}s)`;

      // Forensic blocking flags (same as SmsXmlParser)
      const blockEvidence: string[] = [];
      if (call.type === 5) blockEvidence.push('Call actively rejected');
      if (call.type === 6) blockEvidence.push('Number on refuse/block list');
      if (call.type === 2 && call.duration === 0) blockEvidence.push('Outgoing call with 0 duration - did not connect');
      if (blockEvidence.length > 0) {
        text += ` [FORENSIC FLAG: ${blockEvidence.join(', ')}]`;
      }

      results.push({
        text,
        metadata: {
          timestamp,
          sender,
          recipient,
          raw_address: call.number || '',
          contact_name: call.contact_name || 'Unknown',
          record_type: 'call',
          raw_data: JSON.stringify(call),
          type_code: String(call.type),
          duration_seconds: String(call.duration),
          result_label: label,
        },
      });
    }

    return results;
  }

  // -----------------------------------------------------------------------
  // Helpers — identical to SmsEvidenceIngestor patterns
  // -----------------------------------------------------------------------

  private bucketConversations(records: NormalizedMessage[]): Map<string, ConversationBucket> {
    const conversations = new Map<string, ConversationBucket>();
    for (const record of records) {
      const participants = this.getParticipants(record);
      const conversationHash = this.sha256(JSON.stringify(participants));

      if (!conversations.has(conversationHash)) {
        conversations.set(conversationHash, {
          id: uuidv7(),
          participants,
          messages: [],
          conversationHash,
        });
      }
      conversations.get(conversationHash)!.messages.push(record);
    }
    return conversations;
  }

  private getParticipants(record: NormalizedMessage): string[] {
    const set = new Set<string>();
    set.add(record.metadata.sender || 'Unknown');
    set.add(record.metadata.recipient || 'Unknown');
    if (record.metadata.raw_address) set.add(record.metadata.raw_address);
    return [...set].filter(Boolean).map((p) => p.trim()).sort((a, b) => a.localeCompare(b));
  }

  private normalizeParticipant(value: string | undefined): string | null {
    if (!value) return null;
    return value.trim().toLowerCase();
  }

  private detectDirection(record: NormalizedMessage): 'inbound' | 'outbound' | 'unknown' {
    const sender = record.metadata.sender.trim().toLowerCase();
    if (sender === 'me') return 'outbound';
    const recipient = record.metadata.recipient.trim().toLowerCase();
    if (recipient === 'me') return 'inbound';
    return 'unknown';
  }

  private detectMessageType(record: NormalizedMessage): string {
    if (record.metadata.record_type === 'call') return 'call';
    if (record.metadata.record_type === 'mms') {
      return record.metadata.has_attachments ? 'media' : 'mms';
    }
    return 'text';
  }

  private parseTimestamp(raw: string): string {
    const ms = parseInt(raw, 10);
    if (!isNaN(ms) && ms > 1_000_000_000_000) {
      // epoch-ms
      return new Date(ms).toISOString();
    }
    if (!isNaN(ms) && ms > 1_000_000_000) {
      // epoch-s
      return new Date(ms * 1000).toISOString();
    }
    // Try ISO parse
    const d = new Date(raw);
    return isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString();
  }

  private sha256(value: string): string {
    return createHash('sha256').update(value).digest('hex');
  }
}
