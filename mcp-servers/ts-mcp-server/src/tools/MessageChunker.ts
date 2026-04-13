import { createHash } from 'crypto';
import { uuidv7 } from 'uuidv7';

/**
 * MessageChunker — splits messages into overlapping chunks for embedding.
 *
 * Short messages (< CHUNK_SIZE) are returned as a single chunk.
 * Longer messages are split on sentence or word boundaries with overlap
 * so that semantic context is preserved across chunk edges.
 *
 * Each chunk receives its own UUIDv7 and SHA-256 content hash for
 * chain-of-custody tracking.
 */

export interface MessageChunk {
  /** UUIDv7 for the chunk */
  id: string;
  /** Parent message ID */
  message_id: string;
  /** Ingestion ID from DuckDB vault */
  ingestion_id: string;
  /** Chunk text */
  text: string;
  /** SHA-256 of the chunk text */
  chunk_hash: string;
  /** Zero-based chunk index within the parent message */
  chunk_index: number;
  /** Total number of chunks for this message */
  chunk_total: number;
  /** Character offset where this chunk starts in the original body */
  start_offset: number;
  /** Character offset where this chunk ends in the original body */
  end_offset: number;
  /** Metadata carried forward from the parent message */
  metadata: {
    sender?: string;
    recipient?: string;
    platform?: string;
    timestamp?: string;
    conversation_id?: string;
  };
}

export interface ChunkerOptions {
  /** Target chunk size in characters (default: 512) */
  chunkSize?: number;
  /** Overlap in characters between consecutive chunks (default: 64) */
  overlap?: number;
}

const DEFAULT_CHUNK_SIZE = 512;
const DEFAULT_OVERLAP = 64;

/**
 * Sentence-boundary regex: split on `.` `!` `?` followed by whitespace,
 * or on newlines. Keeps the delimiter attached to the preceding segment.
 */
const SENTENCE_SPLIT = /(?<=[.!?])\s+|\n+/;

export class MessageChunker {
  private readonly chunkSize: number;
  private readonly overlap: number;

  constructor(options: ChunkerOptions = {}) {
    this.chunkSize = options.chunkSize ?? DEFAULT_CHUNK_SIZE;
    this.overlap = options.overlap ?? DEFAULT_OVERLAP;
  }

  /**
   * Chunk a single message body into one or more MessageChunks.
   */
  chunk(
    body: string,
    messageId: string,
    ingestionId: string,
    metadata: MessageChunk['metadata'] = {},
  ): MessageChunk[] {
    if (!body || body.trim().length === 0) {
      return [];
    }

    const trimmed = body.trim();

    // Short messages → single chunk
    if (trimmed.length <= this.chunkSize) {
      return [
        this.buildChunk(trimmed, 0, 0, trimmed.length, 1, messageId, ingestionId, metadata),
      ];
    }

    // Split into sentences first, then merge into chunk-sized windows
    const sentences = trimmed.split(SENTENCE_SPLIT).filter(Boolean);
    const chunks: MessageChunk[] = [];
    let currentText = '';
    let currentStart = 0;
    let offset = 0;

    for (const sentence of sentences) {
      // If adding this sentence exceeds chunk size, flush
      if (currentText.length > 0 && currentText.length + sentence.length + 1 > this.chunkSize) {
        chunks.push(
          this.buildChunk(
            currentText,
            chunks.length,
            currentStart,
            currentStart + currentText.length,
            -1, // total filled in later
            messageId,
            ingestionId,
            metadata,
          ),
        );

        // Start next chunk with overlap from the tail of the current chunk
        const overlapText = currentText.slice(-this.overlap);
        currentStart = currentStart + currentText.length - overlapText.length;
        currentText = overlapText;
      }

      if (currentText.length === 0) {
        currentStart = offset;
      }

      currentText += (currentText.length > 0 ? ' ' : '') + sentence;
      offset += sentence.length + 1; // +1 for the split delimiter space
    }

    // Flush remaining
    if (currentText.length > 0) {
      chunks.push(
        this.buildChunk(
          currentText,
          chunks.length,
          currentStart,
          currentStart + currentText.length,
          -1,
          messageId,
          ingestionId,
          metadata,
        ),
      );
    }

    // Fill in chunk_total
    for (const chunk of chunks) {
      chunk.chunk_total = chunks.length;
    }

    return chunks;
  }

  /**
   * Chunk an array of messages in batch.
   */
  chunkBatch(
    messages: Array<{
      id: string;
      body: string;
      ingestion_id: string;
      sender?: string;
      recipient?: string;
      platform?: string;
      timestamp?: string;
      conversation_id?: string;
    }>,
  ): MessageChunk[] {
    const allChunks: MessageChunk[] = [];

    for (const msg of messages) {
      const chunks = this.chunk(msg.body, msg.id, msg.ingestion_id, {
        sender: msg.sender,
        recipient: msg.recipient,
        platform: msg.platform,
        timestamp: msg.timestamp,
        conversation_id: msg.conversation_id,
      });
      allChunks.push(...chunks);
    }

    return allChunks;
  }

  private buildChunk(
    text: string,
    index: number,
    startOffset: number,
    endOffset: number,
    total: number,
    messageId: string,
    ingestionId: string,
    metadata: MessageChunk['metadata'],
  ): MessageChunk {
    return {
      id: uuidv7(),
      message_id: messageId,
      ingestion_id: ingestionId,
      text,
      chunk_hash: createHash('sha256').update(text).digest('hex'),
      chunk_index: index,
      chunk_total: total,
      start_offset: startOffset,
      end_offset: endOffset,
      metadata,
    };
  }
}
