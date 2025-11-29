
## what we have build so far:
we have build an ai workflow with python that can generate blog posts based on given topics. 
today we will extend this workflow to support more complex control flow, including parallel execution, conditional steps, and loops.
Here’s a summary 

---

### 1. **Imports and Setup**
- Imports standard libraries: `base64`, `sys`, `os`
- Loads environment variables (like your OpenAI API key) using `dotenv`
- Imports `OpenAI` client and `pydantic` for data validation (though `pydantic` is not used in the shown code)
- Prints the OpenAI API key (for debugging)
- Initializes the OpenAI client

---

### 2. **Helper Functions**
- **`load_file(path)`**: Reads and returns the content of a file. Exits if the file doesn’t exist.
- **`save_file(path, content)`**: Writes content to a file.
- **`generate_article_draft(outline)`**:
  - Loads example blog posts from the example_posts directory.
  - Sends a prompt to OpenAI’s GPT-4o model to generate a blog post draft based on the provided outline and the style of the example posts.
  - Returns the generated markdown content.
- **`generate_thumbnail(article)`**:
  - Uses OpenAI’s image model (`gpt-image-1`) to generate a thumbnail image for the blog post.
  - Decodes the image from base64 and returns it as bytes.

---

### 3. **Main Workflow (`main()` function)**
- Checks for a command-line argument (the outline file path).
- Loads the outline from the provided file.
- Generates a blog post draft using the outline.
- Prints the generated draft.
- Generates a thumbnail image for the blog post.
- Saves the thumbnail image and the blog post draft to files.
- Also saves the draft to a specific path in another project directory.
- Prints confirmation messages for saved files.

---

## Feedback Mechanism

with out existing project management tools, we can set up a feedback mechanism that allows users to report issues or suggest improvements directly from the blog interface. This can be achieved by integrating a feedback form that submits data to our project management system, ensuring that all feedback is tracked and addressed in a timely manner.



Now, when building workflows, no matter if you're using AI or not, and therefore also when you're building AI agents, it's likely that not all
steps need to run one after another, or maybe not all steps should run one after another.

in the last workflow, that's essentially the only case we had, We ran all oursteps in sequence, sequential, which means one step after another, and we did that because many of our steps did depend on each other.

And if step B depends on step A, it of course needs to run after step A. 


but there are case when want to run steps in parallel, or when some steps are independent of each other and therefore can run in any order.
For example, if you have step A that took really long to run, and step B that is independent of step A, you could run step B while waiting for step A to finish.

you could also run steps conditionally, for example, if step A produces a result that indicates that step B should run, then you can run step B, otherwise you skip it.

you could also repeat steps, That might make sense if you wanna refine a result over time, if you gather feedback, or if you are building a chat application where you want to allow the user to ask follow-up questions.

let's go 
 in main, in the infinite loop (but with exit condition), we keep generate_article_draft, but no longer use just outline as input, but also the previous draft (if it exists), and some feedback if it exists.

 after generating the draft, we evaluate it, so we feed the draft to an evaluation function that decides whether the draft needs improvement or not. we call this function evaluate_article_draft. the function will also use ai model to evaluate the draft and provide feedback. we will as for the out put in json format with two fields: needs_improvement (boolean) and feedback (string). and also define the class in our python code using pydantic => strutured output.

```python
 class Evaluation(BaseModel):
    needs_improvement: bool = Field(
        description="Whether the draft needs to be improved"
    )
    feedback: str = Field(description="Feedback on how to improve the draft")
``` 

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




and of course, if the needs_improvement is true, we will use the feedback to generate a new draft, otherwise we will exit the loop and return the final draft ==> always remember to handle the exit condition properly to avoid infinite loops. I also add a var call cycles to limit the number of iterations to avoid infinite loops in case the model keeps saying that the draft needs improvement.

after the loop end, we will do some 2 step in parallel: generate the thumbnail and create a linkedin post about our blog post. we can use the python threading module to run these two steps in parallel.


```python
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_thumbnail = executor.submit(generate_thumbnail, blog_post_draft)
        future_linkedin = executor.submit(generate_linkedin_post, blog_post_draft)

        linkedin_post = future_linkedin.result()
        thumbnail_image = future_thumbnail.result()
```

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

update generate_article_draft to accept feedback and previous draft as input

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

# run and test
* uv sync => to install concurrent package
* python main.py path/to/outline