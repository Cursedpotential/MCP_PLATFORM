"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_js_1 = require("@modelcontextprotocol/sdk/server/index.js");
const stdio_js_1 = require("@modelcontextprotocol/sdk/server/stdio.js");
const types_js_1 = require("@modelcontextprotocol/sdk/types.js");
const SmsXmlReader_js_1 = require("./tools/SmsXmlReader.js");
/**
 * AI DIAL TypeScript Core Server
 * Exposes atomic parsing and relational database operations as MCP tools.
 */
class DialTypeScriptServer {
    server;
    constructor() {
        this.server = new index_js_1.Server({
            name: "dial-ts-core",
            version: "1.0.0",
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.setupToolHandlers();
        // Error handling
        this.server.onerror = (error) => console.error('[MCP Error]', error);
        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }
    setupToolHandlers() {
        this.server.setRequestHandler(types_js_1.ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: "ping",
                    description: "Ping the TS MCP server to verify it is running within DIAL",
                    inputSchema: {
                        type: "object",
                        properties: {},
                    },
                },
                {
                    name: "parse_sms_xml",
                    description: "Parses massive SMS/Call Backup XML files into normalized JSON arrays.",
                    inputSchema: {
                        type: "object",
                        properties: {
                            file_path: {
                                type: "string",
                                description: "The absolute file path to the XML file to parse.",
                            },
                        },
                        required: ["file_path"],
                    },
                },
                // TODO: In subsequent tasks, import and register the actual legacy parsers here.
            ],
        }));
        this.server.setRequestHandler(types_js_1.CallToolRequestSchema, async (request) => {
            if (request.params.name === "ping") {
                return {
                    content: [
                        {
                            type: "text",
                            text: "Pong from dial-ts-core server!",
                        },
                    ],
                };
            }
            if (request.params.name === "parse_sms_xml") {
                const filePath = String(request.params.arguments?.file_path);
                if (!filePath) {
                    throw new Error("file_path argument is required");
                }
                try {
                    const reader = new SmsXmlReader_js_1.SmsXmlReader();
                    const messages = await reader.loadData(filePath);
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify(messages, null, 2),
                            },
                        ],
                    };
                }
                catch (error) {
                    throw new Error(`Failed to parse XML: ${error.message}`);
                }
            }
            throw new Error(`Tool not found: ${request.params.name}`);
        });
    }
    async run() {
        // Uses stdio for communicating with DIAL core over the MCP protocol
        const transport = new stdio_js_1.StdioServerTransport();
        await this.server.connect(transport);
        console.error("DIAL TS MCP Server running on stdio");
    }
}
const server = new DialTypeScriptServer();
server.run().catch(console.error);
//# sourceMappingURL=index.js.map