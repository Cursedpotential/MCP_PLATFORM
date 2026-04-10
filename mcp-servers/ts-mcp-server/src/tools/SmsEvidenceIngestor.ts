import { createHash } from 'crypto';
import { basename } from 'path';
import { readFile, stat } from 'fs/promises';
import { uuidv7 } from 'uuidv7';
import { DuckDbVault } from './DuckDbVault.js';
import { PostgresWriter } from './PostgresWriter.js';
import { NormalizedMessage, SmsXmlParser } from './SmsXmlParser.js';

interface SmsIngestOptions {
  deviceId?: string;
  caseId?: string;
  sourcePlatform?: string;
  extractionMethod?: string;
}

interface ConversationBucket {
  id: string;
  participants: string[];
  messages: NormalizedMessage[];
  conversationHash: string;
}

export class SmsEvidenceIngestor {
  constructor(
    private readonly vault: DuckDbVault,
    private readonly pg: PostgresWriter,
  ) {}

  async ingest(filePath: string, options: SmsIngestOptions = {}) {
    const rawContent = await readFile(filePath, 'utf8');
    const fileStats = await stat(filePath);
    const sourceName = basename(filePath);
    const sourceHash = await this.vault.hashContent(rawContent);
    const existing = await this.vault.getIngestionByHash(sourceHash);

    if (existing) {
      return {
        status: 'duplicate',
        ingestion_id: existing.id,
        source_hash: existing.source_hash,
        source_name: existing.source_name,
      };
    }

    const ingestion = await this.vault.logIngestion(
      'sms_backup_xml',
      sourceName,
      rawContent,
      filePath,
      {
        case_id: options.caseId ?? null,
        device_id: options.deviceId ?? null,
        source_platform: options.sourcePlatform ?? 'sms_backup_restore',
        extraction_method: options.extractionMethod ?? 'export',
        file_size: fileStats.size,
      },
    );

    const parser = new SmsXmlParser();
    const records = await parser.loadData(filePath);

    const documentId = uuidv7();
    await this.pg.writeRecord('evidence.documents', {
      id: documentId,
      filename: sourceName,
      file_hash: sourceHash,
      file_size: fileStats.size,
      file_type: 'application/xml',
      source_platform: options.sourcePlatform ?? 'sms_backup_restore',
      acquisition_method: options.extractionMethod ?? 'export',
      acquisition_date: new Date(fileStats.mtime).toISOString(),
      processing_status: 'parsed',
      message_count: records.length,
      metadata: {
        ingestion_id: ingestion.id,
        source_path: filePath,
        file_hash: sourceHash,
      },
    });

    const conversations = this.bucketConversations(records);

    for (const conversation of conversations.values()) {
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
          source_path: filePath,
        },
      });

      for (const record of ordered) {
        const rawData = JSON.parse(record.metadata.raw_data);
        const body = record.text ?? '';
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
          body,
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
            ? {
                attachment_count: record.metadata.attachment_count,
                has_attachments: true,
              }
            : null,
          provenance: {
            source_hash: sourceHash,
            conversation_hash: conversation.conversationHash,
            source_document_id: documentId,
            source_ingestion_id: ingestion.id,
            source_path: filePath,
            hash_levels: {
              source_hash: sourceHash,
              conversation_hash: conversation.conversationHash,
              content_hash: contentHash,
            },
            record_type: record.metadata.record_type,
            raw_address: record.metadata.raw_address,
            contact_name: record.metadata.contact_name,
            type_code: record.metadata.type_code,
            status_code: record.metadata.status_code,
            read_status: record.metadata.read_status,
            duration_seconds: record.metadata.duration_seconds,
            result_label: record.metadata.result_label,
            message_box: record.metadata.message_box,
            attachment_count: record.metadata.attachment_count,
            has_attachments: record.metadata.has_attachments,
          },
        });
      }
    }

    await this.vault.updateWriteTracking(ingestion.id, 'postgresql', true);

    return {
      status: 'ingested',
      ingestion_id: ingestion.id,
      source_hash: sourceHash,
      document_id: documentId,
      message_count: records.length,
      conversation_count: conversations.size,
    };
  }

  private bucketConversations(records: NormalizedMessage[]): Map<string, ConversationBucket> {
    const conversations = new Map<string, ConversationBucket>();

    for (const record of records) {
      const participants = this.getParticipants(record);
      const conversationHash = this.sha256(JSON.stringify(participants));
      const key = conversationHash;

      if (!conversations.has(key)) {
        conversations.set(key, {
          id: uuidv7(),
          participants,
          messages: [],
          conversationHash,
        });
      }

      conversations.get(key)!.messages.push(record);
    }

    return conversations;
  }

  private getParticipants(record: NormalizedMessage): string[] {
    const participants = new Set<string>();
    const sender = record.metadata.sender || 'Unknown';
    const recipient = record.metadata.recipient || 'Unknown';
    const rawAddress = record.metadata.raw_address || '';

    participants.add(sender);
    participants.add(recipient);
    if (rawAddress) {
      participants.add(rawAddress);
    }

    return [...participants]
      .filter(Boolean)
      .map((participant) => participant.trim())
      .sort((a, b) => a.localeCompare(b));
  }

  private normalizeParticipant(value: string | undefined): string | null {
    if (!value) return null;
    return value.trim().toLowerCase();
  }

  private detectDirection(record: NormalizedMessage): 'inbound' | 'outbound' | 'unknown' {
    const sender = record.metadata.sender.trim().toLowerCase();
    const recipient = record.metadata.recipient.trim().toLowerCase();

    if (sender === 'me') return 'outbound';
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

  private sha256(value: string): string {
    return createHash('sha256').update(value).digest('hex');
  }
}
