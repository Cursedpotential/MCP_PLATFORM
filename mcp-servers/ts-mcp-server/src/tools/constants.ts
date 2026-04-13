/**
 * Shared constants used by multiple ingestors/parsers.
 */

/**
 * Call type codes from SMS Backup & Restore XML format.
 * Used by both SmsXmlParser and SbvIngestor for consistent labeling.
 */
export const CALL_TYPE_LABELS: Record<string, string> = {
  '1': 'Incoming',
  '2': 'Outgoing',
  '3': 'Missed',
  '4': 'Voicemail',
  '5': 'Rejected',      // FORENSIC: Actively rejected
  '6': 'Refused_List',  // FORENSIC: Number on block list
};
