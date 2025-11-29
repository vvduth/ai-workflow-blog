# Building an AI-Powered Blog Post Generator: A Multi-Step Workflow

---

## Introduction

In this article, I'll build  a multi-step AI workflow that automates the generation of blog posts from outlines. This approach demonstrates powerful patterns for working with large language models, including style transfer, output formatting, and robust response handling.

---

## Workflow Overview

The workflow starts by loading a pre-prepared blog post outline. This outline forms the structural backbone for the article. The core component is the `generate_article_draft` function, which orchestrates the generation process.

---

## Learning from Past Content

A key aspect is maintaining consistency with existing content. The system loads several example posts from a dedicated folder—these markdown files serve as reference material to help the AI understand the writing style.

The prompt combines the outline with these examples, guiding the AI to draft a post in the desired style. The output is required in raw Markdown format to facilitate the next steps.

---

## Specifying Output Format

This workflow demands plain text with Markdown formatting. By instructing the model to deliver raw Markdown, we ensure that the output can be saved directly, avoiding unnecessary post-processing.

---

## Using Developer Messages

A notable architectural choice is the use of a two-message input structure when invoking the GPT-4o model. The developer message provides general instructions, while the user message includes the outline and example posts.

OpenAI recently renamed "system messages" to "developer messages," but both are supported. Developer messages have higher priority, making them ideal for overarching guidelines.

---

## Cleaning AI Responses

Despite instructions for raw Markdown, AI models sometimes wrap output in code blocks. A cleaning step checks for this and removes any unnecessary wrappers, ensuring clean Markdown format for the generated post.

---

## What's Next

This article covers the core generation step. Future discussions will explore a feedback mechanism for iterative content refinement.

---

## Implementation Steps

Here's how the process unfolds in code:

1. **Read Outline:** Use script arguments to specify the outline file.
2. **Load File:** A function reads the outline content.
3. **Generate Draft:** The `generate_article_draft` function creates the blog post draft.
4. **Save File:** The draft is saved as a markdown file.

---

```python
def load_file(path: str) -> str:
    if not os.path.exists(path):
        print(f"Error: The file '{path}' does not exist.")
        sys.exit(1)

    print("Loading file:", path)
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def save_file(path: str, content: str) -> None:
    print("Saving file:", path)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
```

---

```python
def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <outline_file>")
        sys.exit(1)

    outline_file = sys.argv[1]
    outline = load_file(outline_file)

    blog_post_draft = generate_article_draft(outline)

    output_file = outline_file.replace(".txt", "_draft.md")
    save_file(output_file, blog_post_draft)

    print(f"Blog post draft saved to '{output_file}'.")
```

---

## Generating Thumbnails

Enhance the workflow by adding thumbnail generation for the blog post. Integrate an image generation model to create a thumbnail based on the post title or description.

```python
def generate_thumbnail(article: str) -> bytes:
    print("Generating thumbnail...")

    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"Generate a thumbnail for the following blog post: {article}",
        n=1,
        output_format="jpeg",
        size="1536x1024"
    )

    image_bytes = base64.b64decode(response.data[0].b64_json)
    return image_bytes
```

---

## Feedback Mechanism

Stay tuned for insights on integrating feedback mechanisms, allowing refinement and iteration in content generation.

---