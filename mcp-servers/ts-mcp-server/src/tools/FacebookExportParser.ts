import { createHash } from 'crypto';
import { readFile } from 'fs/promises';
import { uuidv7 } from 'uuidv7';
import * as cheerio from 'cheerio';

// ============================================================================
// TYPES
// ============================================================================

export interface ParsedFacebookMessage {
  id: string;
  platform: 'facebook';
  sender: string;
  senderNormalized?: string;
  recipient?: string;
  recipientNormalized?: string;
  body: string;
  timestamp: Date;
  direction: 'inbound' | 'outbound' | 'unknown';
  messageType: 'text' | 'media' | 'share' | 'system';
  rawData: Record<string, any>;
  attachments?: Array<{
    filename: string;
    fileType: string;
    mimeType?: string;
  }>;
  externalId?: string;
  conversationId: string;
  threadName?: string;
}

export interface FacebookParseResult {
  messages: ParsedFacebookMessage[];
  conversationId: string;
  participants: string[];
  threadName?: string;
  messageCount: number;
}

// ============================================================================
// DATE PARSING UTILITIES
// ============================================================================

/**
 * Fuzzy date parser (handles Facebook's various timestamp formats)
 */
function parseDateFuzzy(ts: string): Date | null {
  if (!ts) return null;
  
  // Clean the timestamp
  let cleaned = ts.trim();
  
  // Add space before AM/PM if needed
  cleaned = cleaned.replace(/(\d)(am|pm|AM|PM)\b/gi, '$1 $2');
  
  // Try native parsing first
  const parsed = new Date(cleaned);
  if (!isNaN(parsed.getTime())) {
    return parsed;
  }
  
  // Try common Facebook formats
  const formats = [
    /^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4}),?\s+(\d{1,2}):(\d{2})\s*([AP]M)?$/i,
    /^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4}),?\s+(\d{1,2}):(\d{2})\s*([AP]M)?$/i,
    /^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})\s+at\s+(\d{1,2}):(\d{2})\s*([AP]M)?$/i,
  ];
  
  for (const format of formats) {
    const match = cleaned.match(format);
    if (match) {
      // Try parsing with Date
      const attempt = new Date(cleaned);
      if (!isNaN(attempt.getTime())) {
        return attempt;
      }
    }
  }
  
  return null;
}

// ============================================================================
// PARSER CLASS
// ============================================================================

export class FacebookExportParser {
  private ownName: string;
  private maxMessages: number;

  constructor(options: { ownName?: string; maxMessages?: number } = {}) {
    this.ownName = options.ownName || '';
    this.maxMessages = options.maxMessages || 1000000;
  }

  /**
   * Parse Facebook HTML export file
   */
  async parse(filePath: string): Promise<ParsedFacebookMessage[]> {
    const conversationId = uuidv7();
    const participants: Set<string> = new Set();
    const messages: ParsedFacebookMessage[] = [];
    
    // Load HTML file
    const html = await readFile(filePath, 'utf-8');
    const $ = cheerio.load(html);
    
    // Try Structure 1: <div class="message">
    let foundMessages = this.parseStructure1($, conversationId, participants);
    
    // Try Structure 2: Facebook cards <div class="_a6-g">
    if (foundMessages.length === 0) {
      foundMessages = this.parseStructure2($, conversationId, participants);
    }
    
    // Convert to output format
    for (const msg of foundMessages) {
      const direction = this.detectDirection(msg.sender, this.ownName);
      
      const message: ParsedFacebookMessage = {
        id: uuidv7(),
        platform: 'facebook',
        sender: msg.sender,
        senderNormalized: msg.sender.toLowerCase().trim(),
        body: msg.body,
        timestamp: msg.timestamp,
        direction,
        messageType: this.detectMessageType(msg.body),
        rawData: msg.rawData,
        conversationId,
        externalId: createHash('sha256').update(msg.body + msg.timestamp.toISOString()).digest('hex').substring(0, 16),
      };
      
      messages.push(message);
      
      if (messages.length >= this.maxMessages) {
        break;
      }
    }
    
    return messages;
  }

  /**
   * Parse Structure 1: <div class="message">
   */
  private parseStructure1(
    $: cheerio.CheerioAPI,
    conversationId: string,
    participants: Set<string>
  ): Array<{ sender: string; body: string; timestamp: Date; rawData: any }> {
    const messages: Array<{ sender: string; body: string; timestamp: Date; rawData: any }> = [];
    
    $('div.message').each((_, elem) => {
      const $msg = $(elem);
      const $meta = $msg.find('div.meta');
      
      if (!$meta.length) return;
      
      const metaText = $meta.text().trim();
      const match = metaText.match(/^(.*?)\s*[-–]\s*([A-Za-z]+ \d{1,2},? \d{4},?\s+\d{1,2}:\d{2}\s?(?:AM|PM)?)/);
      
      if (!match) return;
      
      const sender = match[1].trim();
      const timestampStr = match[2];
      const timestamp = parseDateFuzzy(timestampStr);
      
      if (!timestamp) return;
      
      const $body = $msg.find('p');
      const body = $body.text().trim();
      
      if (!body) return;
      
      participants.add(sender);
      
      messages.push({
        sender,
        body,
        timestamp,
        rawData: { meta: metaText, html: $msg.html() || '' },
      });
    });
    
    return messages;
  }

  /**
   * Parse Structure 2: Facebook cards <div class="_a6-g">
   */
  private parseStructure2(
    $: cheerio.CheerioAPI,
    conversationId: string,
    participants: Set<string>
  ): Array<{ sender: string; body: string; timestamp: Date; rawData: any }> {
    const messages: Array<{ sender: string; body: string; timestamp: Date; rawData: any }> = [];
    
    $('div._a6-g').each((_, elem) => {
      const $card = $(elem);
      
      const $header = $card.find('div._a6-h');
      const sender = $header.text().trim();
      
      if (!sender) return;
      
      const $body = $card.find('div._a6-p');
      const bodyDivs = $body.find('div').toArray();
      const bodyBits = bodyDivs.map(div => $(div).text().trim()).filter(t => t);
      const body = bodyBits.join(' ') || $body.text().trim();
      
      if (!body) return;
      
      const $next = $card.next('div._3-94._a6-o');
      const $tsTag = $next.find('div._a72d');
      const timestampStr = $tsTag.text().trim();
      const timestamp = parseDateFuzzy(timestampStr);
      
      if (!timestamp) return;
      
      participants.add(sender);
      
      messages.push({
        sender,
        body,
        timestamp,
        rawData: { cardClass: '_a6-g', html: $card.html() || '' },
      });
    });
    
    return messages;
  }

  private detectDirection(sender: string, ownName: string): 'inbound' | 'outbound' | 'unknown' {
    if (!ownName) return 'unknown';
    return sender.toLowerCase().trim() === ownName.toLowerCase().trim() ? 'outbound' : 'inbound';
  }

  private detectMessageType(body: string): 'text' | 'media' | 'share' | 'system' {
    const lower = body.toLowerCase();
    
    if (lower.includes('sent a photo') || 
        lower.includes('sent a video') ||
        lower.includes('sent an attachment') ||
        lower.includes('shared a file')) {
      return 'media';
    }
    
    if (lower.includes('shared a link') ||
        lower.includes('sent a post') ||
        lower.includes('shared a post')) {
      return 'share';
    }
    
    if (lower.includes('created a group') ||
        lower.includes('added') ||
        lower.includes('left the group') ||
        lower.includes('changed the group name')) {
      return 'system';
    }
    
    return 'text';
  }
}
