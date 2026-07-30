/**
 * DistaMate — Demo Data
 * Realistic sample data for demo/no-auth mode
 */

export const DEMO_EMAILS = [
  {
    id: 'demo-1', threadId: 'thread-1',
    subject: 'Q3 Budget Review — Action Required',
    from: 'Sarah Mitchell', fromEmail: 'sarah.mitchell@company.com',
    to: 'you@distamate.app', date: new Date(Date.now() - 1800000).toISOString(),
    snippet: 'Hi, I wanted to follow up on the Q3 budget allocations. We need to finalize the numbers by end of week...',
    body: `Hi,

I wanted to follow up on the Q3 budget allocations. We need to finalize the numbers by end of week. The Finance team has flagged that the marketing budget is 18% over projection.

Could you please review the attached spreadsheet and confirm the revised allocations by Friday?

Action items:
1. Review marketing budget variance
2. Approve or adjust the IT infrastructure line
3. Sign off on the final numbers

Let me know if you have any questions.

Best,
Sarah Mitchell
CFO, Acme Corp`,
    labelIds: ['INBOX', 'UNREAD'], isUnread: true,
    priority: { priority: 'urgent', reason: 'Budget deadline with action required', actionItem: 'Review and approve budget by Friday' }
  },
  {
    id: 'demo-2', threadId: 'thread-2',
    subject: 'Team Standup Notes — July 30',
    from: 'James Okafor', fromEmail: 'james.okafor@company.com',
    to: 'team@company.com', date: new Date(Date.now() - 7200000).toISOString(),
    snippet: 'Hi team, here are today\'s standup notes. Everyone is on track for the sprint...',
    body: `Hi team,

Here are today's standup notes:

✅ Frontend (Lisa): Completed the new dashboard components. PR under review.
🔄 Backend (Mark): Working on the API rate limiting. ETA: tomorrow.
⚠️ QA (Priya): Found 3 critical bugs in the payment flow. Tickets raised.

Blockers: None for most. Mark needs access to the staging environment — IT ticket submitted.

Sprint velocity: On track for 78 points this sprint.

See you all tomorrow!
James`,
    labelIds: ['INBOX'], isUnread: false,
    priority: { priority: 'info', reason: 'Informational standup notes', actionItem: null }
  },
  {
    id: 'demo-3', threadId: 'thread-3',
    subject: 'Partnership Proposal — Urgent Response Needed',
    from: 'Alexandra Chen', fromEmail: 'a.chen@ventures.io',
    to: 'you@distamate.app', date: new Date(Date.now() - 10800000).toISOString(),
    snippet: 'Dear Team, GlobalVentures would like to discuss a strategic partnership. We have an exclusive window...',
    body: `Dear Team,

GlobalVentures is excited to propose a strategic partnership with your organization. We have identified significant synergies between our product lines.

The window for this partnership is exclusive and expires on August 5th.

Proposed terms:
- 25% revenue share on co-branded products
- Joint marketing budget of $500K
- 18-month initial agreement

We'd love to schedule a call at your earliest convenience this week.

Please confirm your interest by replying to this email.

Best regards,
Alexandra Chen
Head of Partnerships, GlobalVentures`,
    labelIds: ['INBOX', 'UNREAD'], isUnread: true,
    priority: { priority: 'urgent', reason: 'Partnership proposal with expiring deadline', actionItem: 'Reply to confirm interest by Aug 5' }
  },
  {
    id: 'demo-4', threadId: 'thread-4',
    subject: 'Monthly Newsletter — August Edition',
    from: 'TechDigest', fromEmail: 'newsletter@techdigest.io',
    to: 'you@distamate.app', date: new Date(Date.now() - 86400000).toISOString(),
    snippet: 'This month in tech: AI breakthroughs, startup funding rounds, and the future of remote work...',
    body: `Welcome to the August edition of TechDigest!

TOP STORIES THIS MONTH:
• OpenAI launches GPT-5 with 10x context window
• Apple acquires AR startup for $2.4B
• Remote work tools market hits $67B valuation
• EU passes landmark AI regulation bill

FUNDING SPOTLIGHT:
FinTech startup Payo raises $120M Series C for B2B payments infrastructure.

See you next month!
— The TechDigest Team`,
    labelIds: ['INBOX'], isUnread: false,
    priority: { priority: 'info', reason: 'Newsletter, no action required', actionItem: null }
  },
  {
    id: 'demo-5', threadId: 'thread-5',
    subject: 'Invoice #INV-2024-089 Due in 3 Days',
    from: 'Billing — CloudHost Pro', fromEmail: 'billing@cloudhost.pro',
    to: 'you@distamate.app', date: new Date(Date.now() - 172800000).toISOString(),
    snippet: 'Your invoice for cloud hosting services is due on August 2nd. Amount: $1,240.00...',
    body: `Dear Customer,

This is a reminder that Invoice #INV-2024-089 is due in 3 days.

Invoice Details:
- Amount: $1,240.00 USD
- Due Date: August 2, 2024
- Services: Cloud Hosting Pro Plan (Monthly)

Please ensure payment is made to avoid service interruption.

Pay Now: https://cloudhost.pro/pay/INV-2024-089

Thank you,
CloudHost Pro Billing Team`,
    labelIds: ['INBOX', 'UNREAD'], isUnread: true,
    priority: { priority: 'action', reason: 'Invoice due in 3 days', actionItem: 'Pay invoice $1,240 by Aug 2' }
  },
  {
    id: 'demo-6', threadId: 'thread-6',
    subject: 'Re: Product Roadmap Discussion',
    from: 'Marcus Webb', fromEmail: 'marcus@product.co',
    to: 'you@distamate.app', date: new Date(Date.now() - 259200000).toISOString(),
    snippet: 'Great points from yesterday\'s call. I\'ve updated the roadmap doc with the Q4 features we discussed...',
    body: `Great points from yesterday's call!

I've updated the roadmap doc with the Q4 features we discussed. Key additions:
- AI-powered analytics dashboard (High priority)
- Mobile app v2.0 (Medium priority)
- API v3 with GraphQL support (Low priority for Q4, Q1 target)

Can you review and add your comments before the board meeting on Thursday?

Link to doc: https://docs.google.com/document/d/demo-roadmap

Marcus`,
    labelIds: ['INBOX'], isUnread: false,
    priority: { priority: 'action', reason: 'Document review needed for Thursday meeting', actionItem: 'Review roadmap doc before Thursday board meeting' }
  },
];

export const DEMO_FILES = [
  { id: 'file-1', name: 'Q3 Budget Spreadsheet', mimeType: 'application/vnd.google-apps.spreadsheet', modifiedTime: new Date(Date.now() - 3600000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-2', name: 'Product Roadmap Q4 2024', mimeType: 'application/vnd.google-apps.document', modifiedTime: new Date(Date.now() - 7200000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-3', name: 'Marketing Campaigns', mimeType: 'application/vnd.google-apps.folder', modifiedTime: new Date(Date.now() - 86400000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-4', name: 'Partnership Proposal — GlobalVentures.pdf', mimeType: 'application/pdf', modifiedTime: new Date(Date.now() - 172800000).toISOString(), size: '2457600', webViewLink: '#' },
  { id: 'file-5', name: 'Team Performance Review', mimeType: 'application/vnd.google-apps.spreadsheet', modifiedTime: new Date(Date.now() - 259200000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-6', name: 'Brand Assets', mimeType: 'application/vnd.google-apps.folder', modifiedTime: new Date(Date.now() - 345600000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-7', name: 'Investor Presentation Aug 2024', mimeType: 'application/vnd.google-apps.presentation', modifiedTime: new Date(Date.now() - 432000000).toISOString(), size: null, webViewLink: '#' },
  { id: 'file-8', name: 'Employee Handbook 2024.docx', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', modifiedTime: new Date(Date.now() - 604800000).toISOString(), size: '512000', webViewLink: '#' },
  { id: 'file-9', name: 'Architecture Diagram.png', mimeType: 'image/png', modifiedTime: new Date(Date.now() - 864000000).toISOString(), size: '1048576', webViewLink: '#' },
  { id: 'file-10', name: 'Meeting Notes — Board July', mimeType: 'application/vnd.google-apps.document', modifiedTime: new Date(Date.now() - 1209600000).toISOString(), size: null, webViewLink: '#' },
];

export const DEMO_DOC = {
  documentId: 'demo-doc-1',
  title: 'Product Roadmap Q4 2024',
  body: {
    content: [
      { paragraph: { elements: [{ textRun: { content: 'Product Roadmap — Q4 2024\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'Executive Summary\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'This document outlines the strategic product initiatives for Q4 2024, focusing on AI-powered analytics, mobile expansion, and API modernization. The primary goal is to increase user retention by 25% and expand enterprise clients by 40%.\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'Key Initiatives\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: '1. AI Analytics Dashboard — Launch by October 15. Owner: Product Team. Budget: $120,000.\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: '2. Mobile App v2.0 — Launch by November 30. Owner: Mobile Team. Budget: $85,000.\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: '3. GraphQL API v3 — Q1 2025 target. Owner: Backend Team. Budget: $60,000.\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'Action Items\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: '- Sarah to approve budget allocations by August 5\n- Marcus to finalize feature specs by August 10\n- Engineering kickoff meeting scheduled for August 15\n- Board review on Thursday at 2 PM EST\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'Key Stakeholders\n' } }] } },
      { paragraph: { elements: [{ textRun: { content: 'Marcus Webb (Product), Sarah Mitchell (Finance), James Okafor (Engineering), Lisa Tran (Design)\n' } }] } },
    ]
  }
};

export const DEMO_SHEET = {
  meta: {
    spreadsheetId: 'demo-sheet-1',
    properties: { title: 'Q3 Budget Spreadsheet' },
    sheets: [{ properties: { title: 'Budget Overview' } }, { properties: { title: 'Actuals' } }]
  },
  values: [
    ['Department', 'Budgeted ($)', 'Actual ($)', 'Variance ($)', 'Variance %', 'Status'],
    ['Marketing', '250,000', '295,000', '-45,000', '-18%', '⚠️ Over'],
    ['Engineering', '380,000', '362,000', '18,000', '+4.7%', '✅ Under'],
    ['Sales', '180,000', '178,500', '1,500', '+0.8%', '✅ Under'],
    ['Operations', '120,000', '124,000', '-4,000', '-3.3%', '🔄 Slight Over'],
    ['HR', '90,000', '88,000', '2,000', '+2.2%', '✅ Under'],
    ['IT Infrastructure', '75,000', '79,500', '-4,500', '-6%', '🔄 Slight Over'],
    ['Legal', '45,000', '43,000', '2,000', '+4.4%', '✅ Under'],
    ['TOTAL', '1,140,000', '1,170,000', '-30,000', '-2.6%', '⚠️ Over Budget'],
  ]
};
