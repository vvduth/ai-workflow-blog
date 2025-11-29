# Building an AI-Powered Blog Post Generator: A Multi-Step Workflow

In this article, I'll build a multi-step AI workflow (or multi-agent system, if you prefer) that automatically generates blog posts from outlines. This workflow demonstrates several powerful patterns for working with large language models, including style transfer, output formatting, and robust response handling.

## Workflow Overview

The workflow begins by loading a blog post outline that I've prepared. This outline serves as the structural foundation for the article we want to generate. The core of the system is a `generate_article_draft` function that orchestrates the AI generation process.

## Learning from Past Content

One of the most interesting aspects of this approach is how it maintains consistency with my existing content. The workflow loads several example posts from a dedicated folder—these are markdown files of blog posts I've written in the past. These examples aren't used as templates to copy from, but rather as reference material that helps the AI understand my writing style.

The prompt combines the outline with these example posts and instructs the AI to write a detailed blog post based on the outline while adopting the language, tone, and style of the examples. The key instruction is to return the result in raw Markdown format—this is crucial for the next steps in the workflow.

## Specifying Output Format

While we've covered structured data outputs in previous examples, this workflow requires something different: plain text with Markdown formatting. By explicitly instructing the model to return raw Markdown (not JSON or other structured data), we ensure the output can be directly saved as a markdown file. This specificity in output format instructions is an important detail that prevents unnecessary post-processing.

## Using Developer Messages

An interesting architectural choice in this workflow is the use of a two-message input structure when calling the GPT-4o model. Instead of sending a single prompt, the workflow sends two messages: a developer message (formerly called a system message) and a user message.

The developer message pattern deserves some explanation. OpenAI recently renamed "system messages" to "developer messages" in their newer API, though both `role: system` and `role: developer` are supported. Many AI providers still use the term "system message," and you'll encounter it frequently in documentation and blog posts.

The role designation tells the model the source and priority of the message. Developer messages sit at a higher instruction level than user messages, making them ideal for general guidelines that should persist throughout an interaction. While we haven't used developer messages in earlier examples, they're particularly valuable when managing longer chat histories or when you want to cleanly separate general instructions from specific prompts.

In this case, the general instructions go in the developer message, while the user message contains the outline, example posts, and post-specific instructions. You could merge everything into a single user message, but separating them makes the workflow cleaner and more maintainable.

## Cleaning AI Responses

Even with clear instructions to return raw Markdown, AI models sometimes wrap their output in markdown code blocks (the triple backtick syntax). To handle this, the workflow includes a cleaning step that checks whether the response starts with a code block wrapper and removes it if present.

This defensive programming approach is worth emulating: inspect the output you receive and add cleaning logic as needed. Since you own the code, you have complete control over post-processing. After cleaning, the workflow returns the generated blog post in clean Markdown format, ready for the next step.

## What's Next

This covers the core generation step of the workflow. There's also a feedback mechanism that we'll explore in a future article, which allows for iterative refinement of the generated content.

## let define the process :

* our code has to read the outline from a file priived bby user in the script argumetns.
* our code load the file and read the outline content.
* our code will generate the blog post draft based on the outline content.
* our code will save the blog post draft to a markdown file.

so, in main, we need to execute these method/function/logics:
1. read the outline from a file provided by user in the script arguments. => fwe line sof code , no need a separaet func for thisa
2. we load a load_file function to read the outline content from the file path provided , ofc it get the path as argument and return the content of the file. 
3. we need a generate_article_draft function to generate the blog post draft based on the outline content, it get the outline content return by load_file as argument and return the blog post draft content.
4. we need a save_file function to save the blog post draft to a markdown file, it get the blog post draft content and the output file path as arguments.

here are load_file and save_file functions:

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

herr is what our main function will look like:

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
if __name__ == "__main__":
    main()
```

so that the main.py, let go thorugh othrt files&folers for help our workflow generate content
expample_posts/ => to load example posts
 - example1.md
 - example2.md


## adding image thumnail genaration
To enhance our AI-powered blog post generator, we can add a feature to generate a thumbnail image for the blog post. This can be achieved by integrating an image generation model into our workflow. Here's what we need to create:
* a `generate_thumbnail` function that takes the blog post title or a brief description as input and returns a generated image URL or file path.
* * logic to save the thumbnail image to a specified location.
here our updated main function will look like this:

```python
def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <outline_file>")
        sys.exit(1)

    outline_file = sys.argv[1]
    outline = load_file(outline_file)

    blog_post_draft = generate_article_draft(outline)
    print("Generated blog post draft:")
    print(blog_post_draft)

    thumbnail_image = generate_thumbnail(blog_post_draft)
    thumbnail_file = outline_file.replace(".txt", "_thumbnail.jpeg")
    with open(thumbnail_file, "wb") as f:
        f.write(thumbnail_image)
    print(f"Thumbnail saved to '{thumbnail_file}'.")

    output_file = outline_file.replace(".txt", "_draft.md")
    save_file(output_file, blog_post_draft)
    print(f"Blog post draft saved to '{output_file}'.")
```    

```python
def generate_article_draft(outline: str) -> str:
    print("Generating article draft...")
    example_posts_path = "example_posts"

    if not os.path.exists(example_posts_path):
        raise FileNotFoundError(
            f"The directory '{example_posts_path}' does not exist.")

    example_posts = []
    for filename in os.listdir(example_posts_path):
        if filename.lower().endswith(".md") or filename.lower().endswith(".mdx"):
            with open(os.path.join(example_posts_path, filename), 'r', encoding='utf-8') as file:
                example_posts.append(file.read())

    if not example_posts:
        raise ValueError(
            "No example blog posts found in the 'example_posts' directory.")

    example_posts_str = "\n\n".join(
        f"<example-post-{i+1}>\n{post}\n</example-post-{i+1}>"
        for i, post in enumerate(example_posts)
    )

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                # open ai has developer role now, so we can we system or developer
                "role": "developer",
                "content": """
                    You are an expert blog post author who excels at writing engaging educational blog posts.
                    ....
                """
            },
            {
                "role": "user",
                "content": f"""
                    Write a detailed blog post based on the following outline:

                    <outline>
                    {outline}
                    </outline>

                    Below are some example blog posts I wrote in the past:
                    <example-posts>
                    {example_posts_str}
                    </example-posts>

                    Add any addition content here.....
                """
            }
        ]
    )

    generated_text = response.output_text
    # handle if output is wrapped in markdown code block
    if generated_text.strip().startswith("```markdown"):
        lines = generated_text.strip().splitlines()
        if len(lines) > 2 and lines[-1].strip() == "```":
            generated_text = "\n".join(lines[1:-1])

    return generated_text
```

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