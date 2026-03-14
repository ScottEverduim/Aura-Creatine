# Self-Improve Skill

This skill enables the Aura Creatine Autonomous Agent to analyze its own performance, identify areas for improvement, and modify its own codebase to enhance its capabilities. It leverages the `AutonomousCoder` to read, write, execute, and commit code changes.

## Capabilities:

*   **Performance Analysis:** The agent can analyze its `Episodic Memory` and `World State` to identify patterns of success and failure, and pinpoint specific actions or strategies that led to those outcomes.
*   **Goal-Driven Improvement:** Based on identified performance gaps or new opportunities, the agent can generate `AutonomousGoals` related to self-improvement (e.g., "Optimize video generation script for faster execution," "Improve Telegram response accuracy").
*   **Code Modification:** Using the `AutonomousCoder`, the agent can propose and implement changes to its own Python code. This includes:
    *   Reading existing code files.
    *   Generating new code snippets or modifying existing ones (via LLM interaction).
    *   Writing the modified code back to the file system.
    *   Executing tests to validate changes.
    *   Committing validated changes to the GitHub repository.
*   **Reflection and Learning:** After implementing a change, the agent records the outcome in its `Episodic Memory`, allowing it to learn from the success or failure of its self-modifications.

## Usage:

The `Self-Improve` skill is primarily invoked by the `AutonomousBrain` when it detects opportunities for self-optimization during its autonomous cycles. The `AutonomousBrain` will use the `AGIKernel` to access the `AutonomousCoder` functionalities.

### Key Functions:

*   **`analyze_performance()`:** (Internal to AutonomousBrain/AGIKernel) Analyzes memory to find improvement areas.
*   **`propose_code_change(description: str, target_file: str, current_code: str) -> str`:** (Internal, uses LLM) Generates a proposed code change based on a description of the desired improvement, the target file, and its current content. Returns the new code content.
*   **`implement_code_change(file_path: str, new_code_content: str) -> Dict`:** Uses `AutonomousCoder.write_code()` to apply the change.
*   **`test_code_change(file_path: str) -> Dict`:** Uses `AutonomousCoder.execute_code()` to run tests or validate syntax.
*   **`commit_and_push_change(message: str) -> Dict`:** Uses `AutonomousCoder.git_commit_and_push()` to persist changes.

## Workflow Example (Internal Agent Process):

1.  **AutonomousBrain Cycle:** The `AutonomousBrain` runs its `perceive-decide-act-learn` loop.
2.  **Perception:** It perceives a recurring error in video generation (from `Episodic Memory`).
3.  **Decision:** It decides to generate a self-improvement goal: "Fix recurring video generation error."
4.  **Goal Generation:** An `AutonomousGoal` is created with an `action_plan` that includes:
    *   `analyze_error_logs()`
    *   `read_video_generation_script()`
    *   `propose_code_fix(error_details, script_content)`
    *   `implement_code_fix(script_path, proposed_fix)`
    *   `test_video_generation_script()`
    *   `commit_and_push_fix("Fix: Recurring video generation error")`
5.  **Action Execution:** The `AGIKernel` executes these steps, leveraging the `AutonomousCoder` for code-related actions.
6.  **Learning:** The outcome of the fix (success or failure) is recorded in `Episodic Memory`, influencing future behavior and self-improvement strategies.

This skill is foundational for the agent's ability to evolve and adapt without constant human intervention, aligning with the vision of a truly autonomous agent group.
