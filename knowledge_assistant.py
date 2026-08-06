# Imports
import sys
import llm
from rich.console import Console
from rich.markdown import Markdown

# Initialize the console for rich
console = Console()

# Give the AI a detailed system prompt
SYSTEM_PROMPT = (
""
)

model = llm.get_model("llama3.2")
conversation = model.conversation()
response = conversation.prompt(
system=SYSTEM_PROMPT,
temperature=0.3
)
summary_text = response.text()

while True:
    user_input = input(" You: ").strip()

    if not user_input or user_input.lower() in ["exit", "quit", "q", "bye"]:
        console.print("\n[bold cyan]Update finalized. Have a great week![/]")
        break
    with console.status("[bold cyan]Updating report...[/]", spinner="aesthetic", spinner_style="cyan"):
        followup_response = conversation.prompt(user_input)
        followup_text = followup_response.text()

        console.print("\n[bold green]Assistant:[/]")
        console.print(Markdown(followup_text))
        console.print()
