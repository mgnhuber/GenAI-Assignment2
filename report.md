# Report

## Business Use Case

For Assignment 2 I explored a workflow that converts meeting transcripts into structured action items for a project manager. For many teams, meetings produce useful decisions and next steps, but those outcomes are often buried in long notes or informal transcripts. The business goal of this workflow is to reduce the manual effort required to review a transcript, identify follow-up work, and record who owns each task. The intended output is a concise list of action items, each paired with an assigned person or team when that ownership is supported by the transcript.

This use case is valuable because project managers often spend time after meetings doing administrative synthesis rather than higher-value coordination work. Automating the first draft of action-item extraction can save time, improve consistency, and reduce the risk that follow-up work is forgotten. At the same time, the workflow is only useful if it is reliable about ownership and uncertainty, because incorrectly assigned work can create confusion and reduce trust.

## Model Choice

I used `gemini-2.5-flash` for the prototype. I chose it because it was accessible through the Gemini API, fast enough for repeated testing, and capable of returning structured JSON for a narrow extraction task. Earlier in development, the prototype was configured to use `gemini-2.0-flash`, but that model returned a `404 Not Found` response stating that it was no longer available to new users. After switching to `gemini-2.5-flash`, the demo run worked and the system returned usable structured outputs.

I did not complete a broad multi-model comparison in this project. The main comparison I do have is between an unavailable model configuration and the final working configuration. The important practical observation was that model availability and API compatibility matter for reproducibility just as much as prompt quality.

## Baseline vs. Final Design

The baseline design used a short prompt that asked the model to extract action items into a fixed JSON schema and to avoid inventing tasks, owners, or deadlines. That baseline worked on simple cases, but evaluation evidence showed important weaknesses. In the original evaluation output, the system could still hallucinate ownership or apply inconsistent assumptions when the transcript was ambiguous. For example, one evaluation result assigned an owner in a way that was not firmly grounded in the transcript, and another run over the full `eval_set.md` returned a list of case-level outputs that the app was not prepared to summarize.

The final design improved in two ways. First, the prompt was revised to require stronger grounding: owners must appear in the transcript, unnamed speakers should stay `Unassigned`, and ambiguous cases should be marked `needs_review`. Second, the prompt was revised again to explicitly handle the case where the input is a labeled evaluation document with multiple transcript cases. This made the workflow more stable for both single-transcript runs and full evaluation-set runs. In parallel, the app was updated so it could safely print either a single JSON object or a list of JSON results.

The evidence suggests that prompt iteration improved precision and robustness more than recall. The final prompt is better at refusing to over-assign ownership and better at preserving uncertainty. What stayed the same is that the model can still identify clear, explicit action items in straightforward cases. What got slightly worse is that the prompt became longer and more rigid, but for this workflow that tradeoff is acceptable because consistency and auditability matter more than flexibility.

## Remaining Failure Modes and Human Review

The prototype still requires human review in several situations. It can struggle when ownership changes during a conversation, when a task is implied but not explicitly assigned, when a speaker refers to themselves as "I," or when a transcript contains ambiguity such as "someone should do this" or "maybe Ben handles that." It is also possible for the model to convert discussion topics into action items if the wording is close to an assignment. For these reasons, the workflow should be treated as a draft-generation tool rather than a fully autonomous task-tracking system.

## Deployment Recommendation

I would recommend deploying this workflow only with review controls. Specifically, I would use it as an assistant for project managers that generates a first-pass list of action items, highlights uncertain assignments, and requires a human to approve results before they are sent to a task tracker or shared with a team. I would not recommend fully automated deployment where outputs are treated as authoritative without review.

Under those conditions, the workflow is useful. It performs a narrow task clearly, saves time on transcript review, and produces structured output that can support downstream workflows. However, the evaluation results also show that ambiguity and hallucinated ownership remain real risks. In a production setting, the safe deployment path would include human approval, logging of model outputs, periodic evaluation on a stable test set, and clear UI indicators for `needs_review` items.
