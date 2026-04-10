export interface NormalizedMessage {
    text: string;
    metadata: {
        timestamp: string;
        sender: string;
        recipient: string;
        raw_address: string;
        contact_name: string;
        record_type: 'call' | 'message';
        raw_data: string;
    };
}
/**
 * Custom Reader for Massive SMS/Call Backup XML Files
 *
 * Based on legacy logic from `xml-sms-parser.ts` and `enhanced-xml-chunker.py`.
 * Uses stream-processing to handle multi-gigabyte XML files without blowing up RAM.
 */
export declare class SmsXmlReader {
    private parser;
    constructor();
    /**
     * Loads XML data and yields NormalizedMessages.
     * Can handle both <smses> and <calls> root schemas from "SMS Backup & Restore".
     */
    loadData(filePath: string): Promise<NormalizedMessage[]>;
    /**
     * Converts a single raw XML block into a NormalizedMessage
     */
    private parseElementToDocument;
}
//# sourceMappingURL=SmsXmlReader.d.ts.map