# Advanced Control Flow in AI Workflows: Loops, Conditionals, and Parallel Execution

## What We've Built So Far

We've built an AI workflow with Python that generates blog posts based on given topics. The workflow includes several key components:

### Setup and Configuration

The workflow starts by importing standard libraries (`base64`, `sys`, `os`) and loading environment variables using `dotenv`. This is where we store sensitive information like the OpenAI API key. We then import the `OpenAI` client and `pydantic` for data validation, and initialize the OpenAI client for making API calls.

### Core Helper Functions

Our workflow includes several helper functions that handle different parts of the process:

- `load_file(path)` reads and returns the content of a file, exiting if the file doesn't exist
- `save_file(path, content)` writes content to a file
- `generate_article_draft(outline)` loads example blog posts from the `example_posts` directory, sends a prompt to OpenAI's GPT-4o model to generate a blog post draft based on the provided outline and the style of the example posts, and returns the generated markdown content
- `generate_thumbnail(article)` uses OpenAI's image model (`gpt-image-1`) to generate a thumbnail image for the blog post and decodes it from base64

### Main Workflow

The `main()` function orchestrates the entire process. It checks for a command-line argument (the outline file path), loads the outline, generates a blog post draft, prints the draft, generates a thumbnail image, and saves both the thumbnail and the blog post draft to files.

## Today's Goal: Advanced Control Flow

Today we'll extend this workflow to support more complex control flow patterns, including parallel execution, conditional steps, and loops.

## Understanding Sequential vs Parallel Execution

When building workflows, whether you're using AI or not, it's likely that not all steps need to run one after another. In our previous workflow, we ran all steps sequentially because many of them depended on each other. If step B depends on step A, it needs to run after step A finishes.

However, there are cases when you want to run steps in parallel. When some steps are independent of each other, they can run in any order. For example, if step A takes a long time to run and step B is independent of step A, you could run step B while waiting for step A to finish.

You can also run steps conditionally. If step A produces a result that indicates step B should run, then you run step B. Otherwise, you skip it.

You can also repeat steps. This might make sense if you want to refine a result over time, gather feedback, or build a chat application where you want to allow the user to ask follow-up questions.

## Implementing a Feedback Loop

In our updated workflow, we'll add a loop in the main function with an exit condition. We'll keep calling `generate_article_draft`, but instead of using just the outline as input, we'll also pass the previous draft (if it exists) and some feedback (if it exists).

After generating the draft, we'll evaluate it by feeding it to an evaluation function that decides whether the draft needs improvement. We'll call this function `evaluate_article_draft`. The function uses an AI model to evaluate the draft and provide feedback.

### Defining the Evaluation Output Structure

We'll ask for the output in JSON format with two fields: `needs_improvement` (boolean) and `feedback` (string). We'll define this structure in our Python code using Pydantic:

```python
class Evaluation(BaseModel):
    needs_improvement: bool = Field(
        description="Whether the draft needs to be improved"
    )
    feedback: str = Field(description="Feedback on how to improve the draft")
```

### Implementing the Evaluation Function

Here's how we implement the evaluation function:

```python
def evaluate_article_draft(draft: str) -> Evaluation:
    print("Evaluating article draft...")
    response = client.responses.parse(
        model="gpt-4o",
        input=[
            {
                "role": "developer",
                "content": """
                    You are an expert blog post evaluator....
                """,
            },
            {
                "role": "user",
                "content": f"""
                    Evaluate the following blog post draft:
                    <draft>
                    {draft}
                    </draft>

                    Return the feedback as JSON, indicating whether the draft needs to be improved and why.
                """,
            },
        ],
        text_format=Evaluation,
    )

    return response.output_parsed
```

### Handling the Loop

If `needs_improvement` is true, we'll use the feedback to generate a new draft. Otherwise, we'll exit the loop and return the final draft. It's important to handle the exit condition properly to avoid infinite loops. We'll add a variable called `cycles` to limit the number of iterations in case the model keeps saying that the draft needs improvement.

## Running Steps in Parallel

After the loop ends, we'll perform two steps in parallel: generate the thumbnail and create a LinkedIn post about our blog post. We can use Python's threading module to run these steps simultaneously:

```python
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_thumbnail = executor.submit(generate_thumbnail, blog_post_draft)
    future_linkedin = executor.submit(generate_linkedin_post, blog_post_draft)

    linkedin_post = future_linkedin.result()
    thumbnail_image = future_thumbnail.result()
```

### Implementing the LinkedIn Post Generator

Here's the implementation of the LinkedIn post generation function:

```python
def generate_linkedin_post(article: str) -> str:
    print("Generating LinkedIn post...")

    example_posts_path = "example_linkedin_posts"

    if not os.path.exists(example_posts_path):
        raise FileNotFoundError(f"The directory '{example_posts_path}' does not exist.")

    example_posts = []

    for filename in os.listdir(example_posts_path):
        if filename.lower().endswith(".txt"):
            with open(
                os.path.join(example_posts_path, filename), "r", encoding="utf-8"
            ) as file:
                example_posts.append(file.read())

    example_posts_str = "\n\n".join(
        f"<example-post-{i+1}>\n{post}\n</example-post-{i+1}>"
        for i, post in enumerate(example_posts)
    )

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "developer",
                "content": """
                    You are an expert LinkedIn post generator.
                    ....
                """,
            },
            {
                "role": "user",
                "content": f"""
                    Generate a LinkedIn post for the following blog post:
                    <article>
                    {article}
                    </article>

                    Here are some example LinkedIn posts I wrote in the past:
                    <example-posts>
                    {example_posts_str}
                    </example-posts>

                    ...
                """,
            },
        ],
    )

    return response.output_text
```

## Updating the Article Draft Generator

We need to update `generate_article_draft` to accept feedback and the previous draft as input:

```python
def generate_article_draft(
    outline: str, existing_draft: str | None = None, feedback: str | None = None
) -> str:
    print("Generating article draft...")
    example_posts_path = "example_posts"

    if not os.path.exists(example_posts_path):
        raise FileNotFoundError(f"The directory '{example_posts_path}' does not exist.")

    example_posts = []
    for filename in os.listdir(example_posts_path):
        if filename.lower().endswith(".md") or filename.lower().endswith(".mdx"):
            with open(
                os.path.join(example_posts_path, filename), "r", encoding="utf-8"
            ) as file:
                example_posts.append(file.read())

    if not example_posts:
        raise ValueError(
            "No example blog posts found in the 'example_posts' directory."
        )

    example_posts_str = "\n\n".join(
        f"<example-post-{i+1}>\n{post}\n</example-post-{i+1}>"
        for i, post in enumerate(example_posts)
    )

    prompt = f"""
                Write a detailed blog post based on the following outline:
                <outline>
                {outline}
                </outline>
                Below are some example blog posts I wrote in the past:
                <example-posts>
                {example_posts_str}
                </example-posts>
                ...
            """

    if existing_draft and feedback:
        example_posts_str += (
            f"\n\n<existing-draft>\n{existing_draft}\n</existing-draft>"
        )
        example_posts_str += f"\n\n<feedback>\n{feedback}\n</feedback>"

        prompt = f"""
            Write an improved version of the following blog post draft:
            <existing-draft>
            {existing_draft}
            </existing-draft>
            The following feedback should be taken into account when writing the improved draft:
            <feedback>
            {feedback}
            </feedback>
            The original draft AND your improved version should be based on the following outline:
            <outline>
            {outline}
            </outline>
            Below are some example blog posts I wrote in the past:
            <example-posts>
            {example_posts_str}
            </example-posts>
            ....
        """

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "developer",
                "content": """...""",
            },
            {"role": "user", "content": prompt},
        ],
    )

    generated_text = response.output_text

    if generated_text.strip().startswith("```markdown"):
        lines = generated_text.strip().splitlines()
        if len(lines) > 2 and lines[-1].strip() == "```":
            generated_text = "\n".join(lines[1:-1])

    return generated_text
```

## Running and Testing

To run and test the updated workflow:

1. Run `uv sync` to install the `concurrent` package
2. Execute `python main.py path/to/outline`

This workflow now supports loops for iterative improvement, conditional execution based on evaluation results, and parallel execution of independent tasks like thumbnail generation and LinkedIn post creation.
