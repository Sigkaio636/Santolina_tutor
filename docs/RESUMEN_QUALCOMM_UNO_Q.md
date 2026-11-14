# Interpretive summary: UPC Datathon – Qualcomm Challenge setup video (Arduino UNO Q)

This explanation is for our team. It summarizes the organizers' setup video and gives our reading of it.
Where the video and this repository differ, the repository wins, and a note says so.

> **Source:** the transcript of the video "UPC Datathon - Qualcomm Challenge step by step Arduino UNO Q setup"
> ([transcript](https://github.com/Sigkaio636/Santolina_tutor/blob/main/docs/UPC%20Datathon%20-%20Qualcomm%20Challenge%20step%20by%20step%20Arduino%20UNO%20Q%20setup.txt)).
> The speaker is from Qualcomm; the transcript gives his name as "Maros". The video is in English.
> The video walks through the README of the organizers' repository, which is [BOARD_SETUP.md](BOARD_SETUP.md).
> For comparison we also use [CHALLENGE_CONTEXT.md](CHALLENGE_CONTEXT.md).
>
> **How to read this document:** the transcript is automatic and garbles names. What **the video says** is given as said;
> quotes are the transcript's words, lightly cleaned. **My interpretation** is marked *(inferred)*.
> Where the repository settles a fact, a note says "the video says X; the repo has Y".

---

## Summary

- **What is asked:** a *math copilot* that runs **entirely on the Arduino UNO Q**, built on the **M3Kang** dataset (problems from the Kangaroo math competition, "Cangur" in Catalan).
- **It must do one of two things:** (a) teach math or improve the student's experience, or (b) help reason through new problems, or understand why students get specific Kangaroo problems wrong.
- **What to deliver:** a well-documented open-source GitHub repository, a step-by-step write-up on Arduino Project Hub, and a presentation.
- **Hard limit:** the video says the board reads the prompt at about 11 tokens per second (tok/s) and writes at about 5 tok/s. So each answer takes 20–40 s.
  A token is about one short word or part of a word. Our board measured 10.1 tok/s reading and 4.8 tok/s writing ([board reference §14](UNO_Q_BOARD_REFERENCE.md#143-speed)).
- **Accuracy:** the base model gets few right. The speaker says it was wrong about 80% of the time on M3Kang problems.
- **Evaluation:** see [§3](#3-evaluation-criteria) and the open questions in [§6](#6-uncertainties-to-verify).

---

## 1. The challenge

| Point | What the video says |
|---|---|
| Problem | Math proficiency in Catalonia is declining. The goal is to use AI to help students, teachers, or anyone. |
| Data | **M3Kang**, from the Qualcomm Barcelona team. The video calls it a model and a dataset; it is a dataset. The video says almost **2,000 problems** from **2007 to 2024** of the Kangaroo, translated into **108 languages** (the speaker says 106 once). Hosted on Hugging Face. The repo has 1,747 problems in 108 languages ([BOARD_SETUP step 9](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop)). |
| Technical deliverable | Design and build a *math copilot* that **runs entirely on the UNO Q**. |
| Purpose | It must **either teach** students, **or help reason** through new problems, or through why students get certain Kangaroo problems wrong (for example, to prepare for the Proves Cangur). |

The video says the most important thing is to **choose a topic that sparks your curiosity**, and only then the technology.
*(inferred)* The challenge is open: the board and the baseline are the starting point, not the solution.

---

## 2. Project steps

The speaker talks about **12 setup steps plus a step 13 for ideas** ("in a couple of hours you will have everything set up and ready").
These match BOARD_SETUP: steps 0 to 12 set up the board, and [Step 13](BOARD_SETUP.md#step-13-brainstorm-your-idea) is the brainstorm.
The transcript does not number every step. So the table follows the order of the video, and the first column links the BOARD_SETUP step that each row shows.
BOARD_SETUP has the exact commands. The table describes the action, and quotes exact syntax only for standard tools.

| BOARD_SETUP step | What the video does | Why it matters |
|---|---|---|
| [0](BOARD_SETUP.md#step-0-connect-to-the-board) | Install **Arduino App Lab**, connect the UNO Q over **USB-C**, give it a name and a **password**, and enter the UPC Wi-Fi (**eduroam does not work**). Update the OS and the libraries. | The board was made months ago, so its OS and libraries are out of date. **If you lose the password, you can't get into the device.** |
| [0.4](BOARD_SETUP.md#04-if-ssh-doesnt-work-connect-over-usb-with-adb-fallback) | Connect with **ADB** (Android Debug Bridge, a command-line link over the USB cable): `adb devices`, then `adb shell`. With several boards, `adb -s <id> shell`. The video gives SSH as the alternative; BOARD_SETUP uses [SSH first](BOARD_SETUP.md#03-connect-over-ssh), and adb as the fallback. | It is the working channel for the rest of the video. |
| [2](BOARD_SETUP.md#step-2-install-the-build-tools) | `sudo apt-get update`, then install the build packages. | The next step needs compilers. |
| [3](BOARD_SETUP.md#step-3-build-llamacpp) | Download a **specific commit** of **llama.cpp**, build it on the board, and check the versions (`llama-server`, `llama-cli`). | The engine that runs the model on the CPU. |
| [4](BOARD_SETUP.md#step-4-download-the-models) | Download from Hugging Face with `wget`: **Qwen3.5 0.8B** (~1 GB) and an **embedding model** (384 dimensions). The transcript calls it "VGA small"; the repo has bge-small-en-v1.5 (`config.env`). | The language model writes the answer. The embedding model finds similar problems. |
| [5](BOARD_SETUP.md#step-5-hello-world-with-the-language-model) | Start `llama-server` on port **8081**, and test the chat completions API with "what is 7 * 8". Measure the times (in the video: ~6 s predicting and ~9 s on the prompt). | Gives a first speed measurement. |
| [5.6](BOARD_SETUP.md#56-one-letter-a-to-e) | Ask a question with options A–E. It is the toy arithmetic question from BOARD_SETUP, not an M3Kang problem. | Shows that the base model fails: it picks a wrong option. |
| [6](BOARD_SETUP.md#step-6-hello-world-with-the-embedding-model) | Stop the server and start the **embedding** server on port **8082**. Check that it returns vectors of 384 numbers. | The basis of retrieval (RAG): the embedding model turns each problem into numbers, so similar problems can be found. |
| [7](BOARD_SETUP.md#step-7-run-both-models-as-services) | Set up both models as **systemd services**, so they start on their own at boot. systemd is the Linux service manager. The transcript gives the names as "mac lm" and "mac embed"; the repo's model services are `math-llm` and `math-embed`. | No need to start `llama-server` by hand each time. |
| [8](BOARD_SETUP.md#step-8-get-the-datathon-code-and-run-the-first-test) | Clone the **datathon repository** on the board, and run the prediction script (`predict.py`) on sample problems, with the output in a CSV. | Measures the baseline. The language model tends to answer **A or D**. |
| [9](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop), [10](BOARD_SETUP.md#step-10-copy-the-data-to-the-board) | **On the laptop:** create a Python virtual environment, install the requirements, **download M3Kang** (~400 MB; the speaker limits it to ~20 problems to test), and copy the files to the board (`adb push` or `scp`). The video says to use a venv and `pip install`; in this repo, [BOARD_SETUP 9.1](BOARD_SETUP.md#91-install-the-requirements) runs the laptop tools with `uv run --no-project` instead. | Data to build the embeddings and retrieval. |
| [12](BOARD_SETUP.md#step-12-try-retrieval-rag) | Build the **index**: a SQLite file with the embeddings of the problems (the demo has **13 problems**). Then try retrieval with `--rag K` (the video uses `--rag 1`): it adds the K most similar problems, with their answers, to the prompt. | With a similar problem, the answer comes in **under 1 s**; without one, in ~20 s. |
| [Optional: explorer](BOARD_SETUP.md#optional-explore-the-problems-in-your-browser) | **Web interface**: a Python server on the board (host `0.0.0.0`, port **8000**) to browse problems and ask the model from the laptop. | Makes the project visual and easy to demo. The speaker built it with agentic AI. |
| [Explorer: images](BOARD_SETUP.md#let-the-model-see-the-image-experiment) | *(Optional)* **Problems with images:** another `llama-server` on port **8083** with a *projector file*, an extra model file that lets Qwen3.5 0.8B read images. | Many Kangaroo problems have an image. |
| [13](BOARD_SETUP.md#step-13-brainstorm-your-idea) | **Your own project** (the video's "step 13"): build the idea you chose. | That is where the value is. |

**Operational care (said in the video):**

- When you finish, run **`sudo poweroff`** ([BOARD_SETUP 0.5](BOARD_SETUP.md#05-turning-the-board-off)).
  Otherwise `llama-server` can be left stuck when you switch the board on again (the speaker says "in a zombie state").
  Then find it with `pgrep -a llama-server` and stop it with `pkill llama-server` ([BOARD_SETUP, Troubleshooting](BOARD_SETUP.md#troubleshooting)).
- Watch the available **memory**.
- Keeping **two terminals** open (server and tests) helps.

---

## 3. Evaluation criteria

### What the video does NOT say

**There is no explicit rubric**: no weights, no description of who judges, and no required metrics. Any list of "official criteria" would be invented.

### What the speaker stresses *(inferred: these are signals, not rules)*

1. **Curiosity and your own idea:** "choose a topic that actually sparks your curiosity".
2. **Documentation and replicability:** he asks you to explain everything in the repository (which problems you downloaded, how you trained, why you do the project). "Anyone else can replicate your projects anywhere in the world."
3. **Innovation over the baseline:** the base system fails often. That is where you "apply your innovation and creativity".
4. **It works inside the board:** the copilot must run on the UNO Q.

### Metrics proposed by the team (**NOT official**)

From [CHALLENGE_CONTEXT.md §7](CHALLENGE_CONTEXT.md#7-evaluation):

- accuracy on a Kangaroo validation set;
- a pedagogical score (MathTutorBench or MRBench, **which one is not verified**);
- generation checks (language, length, hallucinations);
- on-board metrics (tok/s, time to first token, RAM).

It is the team's own evaluation plan, not a requirement of the challenge.

### Questions for the organizers

Is there an official rubric? How much does the demo weigh against the repository? Are there limits on external or synthetic data?
These questions are in the [pending list of the deliverables checklist](GOAL_MUSTS.md#3-pending-confirmation-with-the-organizers).
Model size is settled: BOARD_SETUP accepts any GGUF model that fits in RAM, answers in time, and has a license you can use ([BOARD_SETUP 13.3](BOARD_SETUP.md#133-ideas-to-reason)).

---

## 4. Available resources

| Type | Resource |
|---|---|
| **Hardware** | Arduino UNO Q 4 GB, connected over USB-C (Mac, Windows or Linux). There is **no** Arduino VENTUNO Q (40 TOPS, trillions of operations per second, a measure of AI compute): "maybe next time in the next datathon". The UNO Q LED matrix. Microphone, webcam and USB hub: the video says to **ask the organizers for them**. BOARD_SETUP allows no external modules: the LED matrix is the only hardware output ([BOARD_SETUP 14.4](BOARD_SETUP.md#144-add-the-led-matrix-and-a-web-page)). |
| **Software** | Arduino App Lab, ADB, llama.cpp, Qwen3.5 0.8B, the embedding model bge-small-en-v1.5. |
| **Data** | M3Kang on Hugging Face (dataset and paper), ~400 MB. |
| **Organizers' repository** | It holds the step-by-step README, the prediction script, the RAG indexer, the web interface, tools to measure and analyze errors, and LED matrix examples. The video gives no URL. The repo has it: [mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq/tree/d6e3f1b0c28a7dc47db3143c17e1e609006cd0a4), and [BOARD_SETUP.md](BOARD_SETUP.md) is its README. |
| **Skills for agents** | A *skills* folder in the repository, so your AI agent knows how to use the UNO Q, build apps for it, use the embedding model and the hardware, and write the project for Project Hub. Advice: **copy them into your own repository**. |
| **References** | See the list below. |
| **Contact** | The speaker offers contact on LinkedIn and by email (the email in the transcript is unclear, so I don't copy it). |

References named in the video:

- A tutorial on RAG with small language models on Arduino, by a teacher from Chile (a Qualcomm ambassador who also teaches in Brazil and Latin America).
  The transcript says "Marel Rob"; BOARD_SETUP names Marcelo Rovai: [Generative AI at the Edge with the UNO Q, RAG chapter](https://mjrovai.github.io/genai-uno-q/content/rag/rag.html).
- The speaker's own article on LLMs and VLMs on the UNO Q with Go: [How to Run High-Performance LLMs Locally on the Arduino UNO Q](https://projecthub.arduino.cc/marc-edgeimpulse/running-local-llms-and-vlms-on-the-arduino-uno-q-with-yzma-74e288).
- The "Island Sword Fight" project on his GitHub (keyword spotting).

---

## 5. Interpretive reading

1. **The bottleneck is speed, not only accuracy.** About 5 tok/s means 20–40 s per answer. Anything that avoids or shortens generation gains a lot.
2. **Retrieval (RAG) is the path Qualcomm demonstrates, and the cheapest lever.** With only 13 problems in the index, a similar question got its answer in under 1 s. With the full dataset, the gain should grow *(inferred)*.
3. **The difference is in the idea and the experience, not in a bigger model.** The board can't run more. The value is in how the copilot is used (classroom debate, accessibility, diagnosing errors).
4. **The speaker values documentation almost as much as the result.** Repository, Project Hub and presentation appear as deliverables. He stresses that anyone should be able to replicate the project.
5. **Divergence from the team's plan.** [CHALLENGE_CONTEXT.md](CHALLENGE_CONTEXT.md) starts from fine-tuning, pruning and quantizing a Gemma model.
   The video demonstrates another path: Qwen3.5 0.8B with embeddings and retrieval, without retraining.
   They don't exclude each other, but the team should **decide on purpose**.
   The deployed language model is Qwen3.5 0.8B Q8_0 (`config.env`); the fine-tune base is not chosen yet, and Gemma 3 is one option being explored.

   | Point | Video | `CHALLENGE_CONTEXT.md` |
   |---|---|---|
   | Number of problems | almost 2,000 (M3Kang, 108 languages) | ~1,000 |
   | Approach | Retrieval and embeddings on Qwen3.5 0.8B | Fine-tuning, pruning and quantization of Gemma |
   | Server | `llama-server` on 8081 / 8082 / 8083 | the same: its own `llama-server` services on 8081 / 8082 / 8083, not the App Lab LLM Brick |

   On the number of problems, the repo has 1,747 ([BOARD_SETUP step 9](BOARD_SETUP.md#step-9-prepare-m3kang-on-your-laptop)).

---

## 6. Uncertainties to verify

- **Evaluation criteria:** the video gives none ([§3](#3-evaluation-criteria)). The question is in the [pending list](GOAL_MUSTS.md#3-pending-confirmation-with-the-organizers).
- **Presentation date:** the video mentions "the presentation that you're going to do on Sundays" and says "I will see your projects on Monday". The date is unclear; it is in the [pending list](GOAL_MUSTS.md#3-pending-confirmation-with-the-organizers).
- **Names the automatic transcript garbles:** "Dathlon" (datathon) and "provis kangur" (Proves Cangur).

Settled by the repository:

- The organizers' repository and its README: [BOARD_SETUP.md](BOARD_SETUP.md), with the exact commands and the real step numbers.
- The embedding model ("VGA small" in the transcript) is bge-small-en-v1.5.
- The model services ("mac lm" / "mac embed") are `math-llm` and `math-embed`.
- The teacher from Chile ("Marel Rob") is Marcelo Rovai.
- M3Kang has 1,747 problems in 108 languages.
- The board is the 4 GB variant (ABX00173). The video only says "you will need a lot of memory". See the [board reference](UNO_Q_BOARD_REFERENCE.md).

---

## 7. What to try

Set up the board with [BOARD_SETUP](BOARD_SETUP.md#the-steps-at-a-glance) steps 0 to 12, including the baseline (step 11) and retrieval (step 12).
Then choose an idea ([Step 13](BOARD_SETUP.md#step-13-brainstorm-your-idea)), and document it while you build.
The deliverables checklist is [GOAL_MUSTS.md](GOAL_MUSTS.md).

**Ideas the speaker proposes (step 13):**

1. **An easier similar problem:** when the student is stuck, the copilot finds (with embeddings) a similar but easier problem.
2. **A classroom debate box:** a problem is projected, students vote A–E from their phone, a button or their voice, and the UNO Q checks the answer. Web interface in Python.
3. **Multilingual bridge and simpler statements:** rewrite the text more simply (for example, to help people with dyslexia).
4. **A–E keyword spotting by voice:** recognize "a, b, c, d, e" with a local model, and show right or wrong on the LED matrix (red or green). It needs a microphone; BOARD_SETUP allows no external modules.
5. **Problems with images:** read the images with the projector file (port 8083).

[BOARD_SETUP 13.2](BOARD_SETUP.md#132-ideas-to-teach) and [13.3](BOARD_SETUP.md#133-ideas-to-reason) describe most of these ideas, and more. 13.2 says how to measure each one.
