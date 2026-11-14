# Deliverables checklist: what the challenge asks

This reference checklist is for our team. It lists what the Qualcomm challenge of Datathon FME 2026 asks each team to deliver.
It is the only deliverables checklist in this repository. Each item cites its source, so you can check it.
Items that no source backs are marked ⚠️ and listed in [Pending](#3-pending-confirmation-with-the-organizers).

Sources:

- [`BOARD_SETUP.md`](BOARD_SETUP.md): the README of the organizers' repository
  [mpous/datathon-UPC-maths-qualcomm-arduino-unoq](https://github.com/mpous/datathon-UPC-maths-qualcomm-arduino-unoq/tree/d6e3f1b0c28a7dc47db3143c17e1e609006cd0a4),
  copied at commit `d6e3f1b`. Sections used: [The challenge](BOARD_SETUP.md#the-challenge),
  [Deliverables](BOARD_SETUP.md#deliverables), [Step 14](BOARD_SETUP.md#step-14-implement-the-idea-and-prepare-the-presentation)
  and [Step 15](BOARD_SETUP.md#step-15-publish-your-project).
- The [`publish-project` skill](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md): structure of the README and of the Project Hub write-up.
- The setup video: a Qualcomm speaker presents the challenge and walks through the board setup.
  [Transcript](https://github.com/Sigkaio636/Santolina_tutor/blob/main/docs/UPC%20Datathon%20-%20Qualcomm%20Challenge%20step%20by%20step%20Arduino%20UNO%20Q%20setup.txt);
  our summary is [RESUMEN_QUALCOMM_UNO_Q.md](RESUMEN_QUALCOMM_UNO_Q.md).
- [`CHALLENGE_CONTEXT.md`](CHALLENGE_CONTEXT.md): the team's context.

> **There is no official rubric.** No weights, no description of who judges, and no required metrics ([video summary §3](RESUMEN_QUALCOMM_UNO_Q.md#3-evaluation-criteria)). This list says what is asked. It does not say how much each item scores. If the organizers publish a rubric, it replaces section 2.

---

## 1. Required checklist

### 1.1 The challenge

- [ ] The copilot **runs entirely on the Arduino UNO Q**, without leaving the device. ([BOARD_SETUP, The challenge](BOARD_SETUP.md#the-challenge))
- [ ] It **uses M3Kang** in its own way. ([BOARD_SETUP, The challenge](BOARD_SETUP.md#the-challenge))
- [ ] It covers **at least one** of the two functions: ([BOARD_SETUP, The challenge](BOARD_SETUP.md#the-challenge))
    - [ ] **Teach**: it guides the student without giving the answer (hints, adaptive practice, error analysis, physical interaction, collaboration).
    - [ ] **Reason**: given a Kangaroo-style problem, it chooses the correct answer. The organizers measure this on a hidden test.
- [ ] The root `predict.py` keeps the organizers' [contract](BOARD_SETUP.md#111-how-the-baseline-works), whichever function the team picks. The organizers score every team's `predict.py` on the hidden test. ([BOARD_SETUP 13.3](BOARD_SETUP.md#133-ideas-to-reason), [`CLAUDE.md`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/CLAUDE.md))

### 1.2 Public GitHub repository

- [ ] The repository is **public** and open source. ([BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository))
- [ ] It holds **everything needed to run the copilot on a fresh UNO Q**: ([BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository), [publish-project, The GitHub repository](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md#the-github-repository))
    - [ ] `config.env` with the repository, revision, file and SHA256 of each model, and the llama.cpp commit.
    - [ ] The service files.
    - [ ] The App Lab app, if there is one. [App Lab](UNO_Q_BOARD_REFERENCE.md#72-arduino-app-lab) is Arduino's editor that builds and runs apps on the UNO Q.
- [ ] It has a **license** for our own code (for example MIT), and credits for what we reused. ([BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository), [publish-project](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md#the-github-repository))
- [ ] It holds **no M3Kang data**: no `train.jsonl`, `val.jsonl`, images or `index.db`. Link the [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang) instead. ([`CLAUDE.md`, red line 1](https://github.com/Sigkaio636/Santolina_tutor/blob/main/CLAUDE.md#red-lines), [BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository))
- [ ] It holds no `*.gguf` models either. ([BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository), [`.gitignore`](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.gitignore))
- [ ] `git status` is checked before every push. ([BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository))

### 1.3 README (in this order)

Source of the order: [publish-project, The GitHub repository](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md#the-github-repository). [BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository) lists the same parts.

- [ ] **What it does**, in two or three sentences, with a photo or a short video of it working on the board. (publish-project; BOARD_SETUP 15.1)
- [ ] **Architecture**: what runs on Linux, what runs on the microcontroller, how the Bridge connects them, which model servers it uses, and how it uses M3Kang. The [Bridge](UNO_Q_BOARD_REFERENCE.md#10-bridge-rpc-mcu-linux) is the link between the Linux side and the microcontroller. (publish-project; BOARD_SETUP 15.1)
- [ ] **How to replicate it**, step by step, from a board set up with [steps 0 to 12 of BOARD_SETUP](BOARD_SETUP.md#the-steps-at-a-glance), with the commands and what you should see. (publish-project; BOARD_SETUP 15.1)
- [ ] **Results**: a table from `results/ablations.csv`, each experiment against the baseline, with accuracy, mean and worst latency, and the number of problems. (publish-project)
- [ ] **Error analysis** by **topic**, **language** and **difficulty (level)**, with the number of problems next to each accuracy, and a few wrong answers explained. (publish-project; [BOARD_SETUP, Deliverables](BOARD_SETUP.md#deliverables))
- [ ] **What didn't work**, and what we would try next. (publish-project; BOARD_SETUP 15.1)
- [ ] **The team**. (publish-project; BOARD_SETUP 15.1)

### 1.4 Step-by-step write-up on Arduino Project Hub

- [ ] A project created on [Arduino Project Hub](https://projecthub.arduino.cc/) with an Arduino account. ([BOARD_SETUP 15.2](BOARD_SETUP.md#152-a-step-by-step-on-arduino-project-hub))
- [ ] Sections: ([publish-project, The Arduino Project Hub write-up](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md#the-arduino-project-hub-write-up); [BOARD_SETUP 15.2](BOARD_SETUP.md#152-a-step-by-step-on-arduino-project-hub) has a similar list)
    - [ ] **Introduction**: who it helps, why it runs offline, a photo or video.
    - [ ] **Components and apps**: UNO Q 4 GB, App Lab, llama.cpp and the models.
    - [ ] **Architecture**: a diagram of the two halves of the board, the Bridge, the model servers, and where M3Kang comes in.
    - [ ] **Step by step**: from a fresh board to the demo, with commands and the expected result. Link to the repository instead of pasting all the code.
    - [ ] **Results and error analysis**.
    - [ ] **What we learned**, and what's next.
- [ ] Photos and screenshots **made by the team**. (publish-project)
- [ ] **M3Kang citation** (Torres-Camps et al., 2026, [arXiv:2601.16218](https://arxiv.org/abs/2601.16218)). (BOARD_SETUP 15.2; publish-project)
- [ ] No M3Kang data is uploaded. To show an example problem, check the license on the dataset card first. (BOARD_SETUP 15.2; publish-project)

### 1.5 Live demo and pitch

- [ ] **A live demo on the board** and **a 3-minute pitch**. ([BOARD_SETUP, Deliverables](BOARD_SETUP.md#deliverables))

The rest of this section is a suggestion from the organizers, not a rule ([BOARD_SETUP 14.5](BOARD_SETUP.md#145-prepare-the-demo-and-the-pitch)).

Suggested pitch structure:

| Part | Time | What |
|---|---|---|
| Problem | 20 s | Who the copilot helps, and why it runs offline |
| Demo | 90 s | The copilot working live, on the board |
| Numbers | 40 s | Accuracy against the 22.5% baseline, latency, error analysis |
| What we learned | 30 s | What didn't work, and what we would do next |

Suggested demo preparation:

- [ ] The demo runs the way the organizers will see it: **Wi-Fi off**, services started at boot, nothing on the laptop doing the work.
  If a web page shows on the laptop, connect it to the board over USB with `adb forward`. That command makes a board port reachable on the laptop through the USB cable.
- [ ] Demo problems **chosen in advance**, and tried on the board the same day.
- [ ] **At least two rehearsals with a timer.**
- [ ] **A short video of the demo working**, in case it fails on stage.

### 1.6 Checks before sharing

- [ ] Every number in the README comes from an experiment recorded in `ablations.csv`, on stated problems. If they are 50 or fewer, say so. ([publish-project, The GitHub repository](https://github.com/Sigkaio636/Santolina_tutor/blob/main/.claude/skills/publish-project/SKILL.md#the-github-repository))
- [ ] Baseline reference: **22.5% on 40 English problems whose options OCR read**. OCR (optical character recognition) reads the A to E options from the problem image. (publish-project; [BOARD_SETUP 14.5](BOARD_SETUP.md#145-prepare-the-demo-and-the-pitch))
- [ ] Clone the repository into a new folder and follow the README. Fix every step that fails. (publish-project; [BOARD_SETUP 15.1](BOARD_SETUP.md#151-a-public-github-repository))
- [ ] Every link works. (publish-project)
- [ ] **Both links go to the organizers**: the repository and the Project Hub write-up. ([BOARD_SETUP, Step 15](BOARD_SETUP.md#step-15-publish-your-project))

---

## 2. Open, subjective and creative fields

Here the sources set no result and no criterion. The team decides, and nobody has said how it is scored. The right-hand column is a suggestion to reduce the risk, not a rule of the challenge.

| Field | Why it is open | What the team decides | Suggestion (not a rule) |
|---|---|---|---|
| **Use of M3Kang** | "How you use M3Kang is up to you": a retrieval knowledge base, a training set, problem embeddings, a difficulty map, a multilingual bridge, "or something nobody has thought of yet". "The most original uses will score highest." ([BOARD_SETUP, The challenge](BOARD_SETUP.md#the-challenge)) | What role M3Kang plays, and why. | Explain it in the README architecture and in the pitch. Measure its effect with an experiment recorded in `ablations.csv`. |
| **Teach or Reason** | One of the two is enough. The organizers score every team's `predict.py` on the hidden test anyway ([BOARD_SETUP 13.3](BOARD_SETUP.md#133-ideas-to-reason)). Teach has no defined metric. | Which one we cover, or both. | For Teach, decide first how to check that it "guides without giving the answer". |
| **The idea and the experience** | The setup video proposes ideas: an easier similar problem, a classroom debate box, simpler problem statements, A–E by voice with the LED matrix, problems with images. They are inspiration, not a closed list. | What the student experiences. | Pick one idea and take it all the way to the demo, rather than several half-done. |
| **Technical approach** | The setup video demonstrates retrieval (RAG) on Qwen3.5 0.8B: the embedding model finds similar solved problems, and they go into the prompt. [`CHALLENGE_CONTEXT.md`](CHALLENGE_CONTEXT.md) plans to fine-tune, prune and quantize a Gemma model. The two do not exclude each other. The deployed language model is Qwen3.5 0.8B Q8_0 (`config.env`); the fine-tune base is not chosen yet, and Gemma 3 is one option being explored. | Which path, and in what order. | Decide it on purpose, and write down why. |
| **Pedagogical quality** | There is no official benchmark. [`CHALLENGE_CONTEXT.md` §7](CHALLENGE_CONTEXT.md#7-evaluation) suggests MathTutorBench or MRBench, not verified. It is our own evaluation plan, not a requirement. | What a "good explanation" is, and how to measure it. | Evaluate open-ended generation, not only A–E accuracy. Pruning and quantization can break generation without lowering multiple-choice accuracy. |
| **Hardware and interface** | The 8×13 LED matrix is the only hardware output ([BOARD_SETUP 14.4](BOARD_SETUP.md#144-add-the-led-matrix-and-a-web-page)). App Lab, a web page and voice are optional. | Whether there is an interface, and which kind. | Give priority to what works on the board without a laptop. |
| **Language** | The response language is not confirmed. | Which languages the copilot speaks. | Confirm with the organizers, and measure the errors by language. |
| **Story and writing** | Our [video summary](RESUMEN_QUALCOMM_UNO_Q.md#5-interpretive-reading) reads the speaker as valuing documentation almost as much as the result. That is an interpretation. The speaker does say that "anyone else can replicate your projects anywhere in the world" (transcript). | How we tell the project, including what failed. | Write for a student who was not at the datathon, in short sentences. Report what didn't work as clearly as what did. |
| **Demo and pitch** | Judged live, by people. | Which problems, in what order, and what to highlight. | Rehearse with a timer, and bring the backup video. |

---

## 3. Pending confirmation with the organizers

- [ ] ⚠️ **Rubric**: neither the setup video nor BOARD_SETUP gives one. ([video summary §3](RESUMEN_QUALCOMM_UNO_Q.md#3-evaluation-criteria))
- [ ] ⚠️ **Weight of the demo against the repository**, and **rules on external and synthetic data**. ([video summary §3](RESUMEN_QUALCOMM_UNO_Q.md#3-evaluation-criteria), [`CHALLENGE_CONTEXT.md` §9](CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist))
- [ ] ⚠️ **Presentation date**: the setup video mentions "the presentation that you're going to do on Sundays" and says "I will see your projects on Monday" (transcript).
- [ ] ⚠️ **Response language(s)** of the copilot. ([`CHALLENGE_CONTEXT.md` §1](CHALLENGE_CONTEXT.md#1-the-challenge-what-we-know) and [§9](CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist))
- [ ] ⚠️ **Which pedagogical benchmark**, and whether there is an official evaluation script. ([`CHALLENGE_CONTEXT.md` §7](CHALLENGE_CONTEXT.md#7-evaluation) and [§9](CHALLENGE_CONTEXT.md#9-open-questions-todo-checklist))
