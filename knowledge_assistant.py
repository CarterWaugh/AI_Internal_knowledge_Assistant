# Imports
import os
import llm
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Initialize rich console for formatted terminal output
rich_console = Console()

KNOWLEDGE_MANIFEST_FILE_PATH = "internal_knowledge_files.txt"
TARGET_LLM_MODEL_NAME = "llama3.2"


def load_knowledge_base(manifest_file_path):
    """
    Reads the list of text file paths from the manifest file and loads their contents.
    Returns a dictionary mapping document filenames to their raw text content.
    """
    loaded_documents = {}

    if not os.path.exists(manifest_file_path):
        rich_console.print(f"[bold red]Error:[/] Manifest file '{manifest_file_path}' was not found.")
        return loaded_documents

    with open(manifest_file_path, "r", encoding="utf-8") as manifest_file_handle:
        target_document_filenames = [
            line_text.strip()
            for line_text in manifest_file_handle
            if line_text.strip()
        ]

    for document_filename in target_document_filenames:
        if os.path.exists(document_filename):
            with open(document_filename, "r", encoding="utf-8") as document_file_handle:
                loaded_documents[document_filename] = document_file_handle.read()
        else:
            rich_console.print(
                f"[bold yellow]Warning:[/] Knowledge file '{document_filename}' listed in manifest was not found."
            )

    return loaded_documents


def build_system_prompt(loaded_documents):
    """
    Combines loaded document contents into a structured context block with line numbers
    and returns a detailed system prompt instructing the AI Assistant to cite source filenames
    and starting line numbers.
    """
    formatted_knowledge_context = ""
    for document_name, document_text in loaded_documents.items():
        document_lines = document_text.splitlines()
        line_numbered_text = "\n".join(
            f"[Line {line_number + 1}] {line_content}"
            for line_number, line_content in enumerate(document_lines)
        )
        formatted_knowledge_context += f"\n--- DOCUMENT: {document_name} ---\n{line_numbered_text}\n"

    constructed_system_prompt = f"""You are the Nexus Tech Solutions Internal AI Knowledge Assistant.
Your mission is to help employees by providing accurate, helpful, and concise answers based strictly on the internal documents provided below.

Guidelines & Source Citation Rules:
1. Always base your answers strictly on the provided internal documentation.
2. MANDATORY CITATION: For every piece of information, policy, or answer you provide, you MUST specify the source document filename and the starting line number where the information is located in the text (e.g., `[Source: employee_handbook.txt, Line 8]` or `(it_and_security_guide.txt, Line 15)`).
3. If a user's question cannot be answered using the provided documents, state clearly that the information is not covered in the internal knowledge base.
4. Use clear formatting (bullet points, bold text, code blocks) to make your responses clean and easy to read.

INTERNAL KNOWLEDGE BASE (Line-Numbered):
{formatted_knowledge_context}
"""
    return constructed_system_prompt


def main():
    """Main execution loop for the Internal Knowledge Assistant."""
    loaded_knowledge_documents = load_knowledge_base(KNOWLEDGE_MANIFEST_FILE_PATH)
    system_instruction_prompt = build_system_prompt(loaded_knowledge_documents)

    # Display welcome header and list loaded documents
    rich_console.print(
        Panel.fit(
            "[bold cyan]Nexus Tech Solutions - Internal AI Knowledge Assistant[/]\n"
            f"[dim]Loaded {len(loaded_knowledge_documents)} document(s) from {KNOWLEDGE_MANIFEST_FILE_PATH}[/dim]",
            border_style="cyan"
        )
    )

    if loaded_knowledge_documents:
        for document_filename in loaded_knowledge_documents.keys():
            rich_console.print(f"  [green]+[/] [bold]{document_filename}[/]")

    rich_console.print("\n[dim]Type your question or 'exit'/'quit' to end the session.[/dim]\n")

    # Initialize model and conversation session
    llm_language_model = llm.get_model(TARGET_LLM_MODEL_NAME)
    chat_conversation_session = llm_language_model.conversation()

    # Interactive Q&A loop
    while True:
        try:
            user_query_input = input(" You: ").strip()
        except (EOFError, KeyboardInterrupt):
            rich_console.print("\n[bold cyan]Session ended. Have a great day![/]")
            break

        if not user_query_input or user_query_input.lower() in ["exit", "quit", "q", "bye"]:
            rich_console.print("\n[bold cyan]Session ended. Have a great day![/]")
            break

        with rich_console.status(
            "[bold cyan]Searching knowledge base...[/]",
            spinner="aesthetic",
            spinner_style="cyan"
        ):
            model_response = chat_conversation_session.prompt(
                user_query_input,
                system=system_instruction_prompt
            )
            assistant_response_text = model_response.text()

        rich_console.print("\n[bold green]Assistant:[/]")
        rich_console.print(Markdown(assistant_response_text))
        rich_console.print()


if __name__ == "__main__":
    main()


