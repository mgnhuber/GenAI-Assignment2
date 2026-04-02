# Evaluation Set

This evaluation set is designed to test a workflow that converts meeting transcripts into action items with assigned owners. Each case includes a representative input and a short note describing what a strong output should do.

## Case 1: Normal Case

**Input**

Team Sync Transcript:
"Let's finalize the launch checklist by Friday. Jordan, please update the customer email draft and send it to marketing for review. Priya will confirm the webinar date with the sales team. I will handle the final budget approval. We should also revisit the onboarding slides next week, but no one is assigned to that yet."

**What a good output should do**

A good output should extract the clear action items, assign Jordan, Priya, and the speaker to their respective tasks, and avoid turning the unassigned note about onboarding slides into a falsely assigned action item.

## Case 2: Edge Case

**Input**

Short Transcript:
"Thanks everyone. Great progress this week. No follow-up actions for now. We'll reconnect on Monday."

**What a good output should do**

A good output should return no action items or explicitly state that no action items were identified. It should not invent tasks just because a meeting occurred.

## Case 3: Likely Failure or Hallucination Case

**Input**

Ambiguous Transcript:
"Someone should probably clean up the dashboard before the client sees it. Also, the API docs need work. Let's make sure it all gets done soon."

**What a good output should do**

A good output should identify that tasks are mentioned but ownership is unclear. It should avoid hallucinating a specific assignee and should flag the result for human review or mark the owner as unassigned.

## Case 4: Multi-Team Representative Case

**Input**

Cross-Functional Meeting Transcript:
"Engineering will fix the login timeout bug before the next release. Design will deliver the updated mobile mockups by Thursday. Customer Success should prepare a short FAQ for known onboarding issues. Marcus is responsible for sending the final release notes to leadership."

**What a good output should do**

A good output should capture both team-owned and individually owned action items, preserve the different owners correctly, and keep the action descriptions specific and concise.

## Case 5: Human Review Needed Case

**Input**

Messy Transcript:
"I think Nina said she could maybe take the vendor contract follow-up, unless legal already owns that. Ben was going to send the revised timeline, or maybe that was for next month. Anyway, we need the security questionnaire completed before procurement can move."

**What a good output should do**

A good output should separate clear tasks from uncertain ones, preserve ambiguity where the transcript is unclear, and signal that some assignments or deadlines need human confirmation instead of confidently guessing.
