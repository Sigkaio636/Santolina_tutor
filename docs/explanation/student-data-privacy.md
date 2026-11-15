# Student data: what a teacher may collect

Santolina is classroom math software. A teacher app runs on the teacher's laptop. An Arduino UNO Q board serves a student app over its own Wi-Fi to students' phones. Students log in with a short code, not their name. Santolina is a proof of concept and will not be used with real students. This page asks a "what if". If a school in Catalonia used it, what could the teacher legally collect? And how does that compare with what the app collects today?

!!! warning "Not legal advice"
    This is a reading of the main texts by a datathon team, made in November 2026. A real deployment needs the school's data protection officer.

## The rules that apply

**The General Data Protection Regulation (GDPR)** (EU Regulation 2016/679) applies to any personal data. A student code is still personal data: the teacher's laptop links it to a name, so the data is pseudonymised, not anonymous.

**Spanish Education Act (LOE), additional provision 23**, "Datos personales de los alumnos" ([consolidated text in the BOE, Spain's official gazette](https://www.boe.es/buscar/act.php?id=BOE-A-2006-7899)). It is the key text for schools. Its paragraphs are called apartados:

- Schools may collect the student data "necesarios para el ejercicio de su función educativa" (needed for their educational function). The text lists family and social background and personal characteristics. It also lists "desarrollo y resultados de su escolarización" (the progress and results of their schooling). Last, it lists other circumstances needed to teach and guide students (apartado 1).
- Enrolment implies this processing. The data must be "la estrictamente necesaria para la función docente y orientadora" (only what teaching and guidance strictly need). It cannot be used "con fines diferentes del educativo sin consentimiento expreso" (for purposes other than education without express consent) (apartado 2).
- Staff with access are bound by secrecy, and the school must apply security measures (apartado 3).

**Spanish Data Protection Act (LOPDGDD, Organic Law 3/2018).** Under Article 7, a child can consent to the use of their data from age 14. Below 14, consent comes from parents or guardians. See the [FAQ on minors and education](https://www.aepd.es/preguntas-frecuentes/10-menores-y-educacion) of the Spanish Data Protection Agency (AEPD).

**The AEPD's guide for schools** ([AEPD, *Guía para centros educativos*](https://www.aepd.es/guias/guia-centros-educativos.pdf)):

- "Por regla general, los centros educativos no necesitan el consentimiento" (as a rule, schools do not need consent) for the educational function.
- Schools must always **inform** families and students, clearly. Consent is needed only for purposes beyond education, explained one by one.
- Schools must know an app's privacy policy and conditions **before** using it, and reject apps that don't offer enough guarantees. A provider that handles data for the school is a processor and needs a contract.
- Data is kept only as long as needed for its purpose.

**The Catalan Data Protection Authority (APDCAT)** oversees Catalan public schools. It publishes data protection guidelines for schools on [its website](https://www.apdcat.cat). The Departament d'Educació's [own guide](https://documents.espai.educacio.gencat.cat/IPCNormativa/DOIGC/GEST_Proteccio_dades.pdf) notes that some processing needs a **data protection impact assessment** (DPIA).

**EU AI Act** (Regulation 2024/1689), [Annex III, point 3](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3):

- AI systems used to **evaluate learning outcomes, including when those outcomes steer the learning process** of students, are **high-risk** (point 3(b)).
- [Article 5(1)(f)](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5) **bans emotion recognition** in education, except for medical or safety reasons.

### What follows for a teacher

1. **The school decides, not the teacher alone.** The school (or the Departament, for public schools) is the controller. The controller is the body that decides why and how to process the data. It must approve the tool before use.
2. **No consent is needed for learning data used to teach**: answers, results, progress, difficulties. Families and students must still be told what is collected and why.
3. **Consent is needed for anything else**: research, a datathon analysis, publishing results, showing a student's work outside class. Below 14, the consent comes from parents or guardians.
4. **Only what is strictly necessary**, kept only as long as needed, kept secure, with no other use.
5. **Adaptive AI is regulated.** An AI system that grades answers, or that chooses the next problem from them, is close to Annex III point 3(b).

## What Santolina collects, compared

| What we collect | Today | Legal reading | Verdict |
| --- | --- | --- | --- |
| Name, group, notes (teacher's laptop only) | Yes | Basic school data, covered by the educational function | OK |
| Pseudonymous student code on the board, never the name | Yes | Good practice: the board holds no names | Good |
| Answers, right/wrong, attempt number, time per exercise | Yes | "Desarrollo y resultados de su escolarización" (progress and results of schooling): core educational data | OK |
| Clues used, solution shown, exercises left unsolved | Yes | Shows where a student struggles: needed for "orientación" (guidance) | OK |
| Free-form chat questions to the [tutor model](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) ("copilot" in the app), and its replies (full text) | Yes | Useful to see doubts, but a child may write anything, including personal or health information. Not strictly necessary in full | Reduce |
| Automatic label of most chat messages: the kind of help asked (`STUCK`, `CONCEPT`, `ATTEMPT`, `SOLUTION`, `OTHER`), from a keyword rule in `student_app/router.py` | Yes | Learning data about the student's difficulties, and much less than the full text | OK |
| Reply times, token counts (reply length) and which part wrote each reply | Yes | Technical data about the tutor model's replies | OK |
| Screens opened (`view_opened`), app language, why a session ended, and the board's time of every event | Yes | Technical and usage data: it dates the sessions and shows the progress, like the phone's clock | OK |
| Leaving the page for another app (`page_hidden`/`page_visible`, seconds away) | Yes | Behavioural monitoring of attention. Hard to call "strictly necessary" | Drop |
| Photos sent with a question | Size and type only, image not stored | Only what is needed (point 4 above) | Good |
| Phone's clock at login | Yes | Technical, needed to date sessions | OK |
| IP address, device model, location | Not stored by the app. The student app keeps the phone's IP address in memory only, to show whether a phone is connected. | — | Good |
| [Learning path](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) that picks an easier problem after a failure | Yes: a fixed rule, no language model. The topic of the next problem comes from the retrieval index's vectors. The student app judges an answer by comparing the chosen letter with the stored answer. | No model evaluates learning outcomes today. A model that grades answers or picks the next problem would move it towards AI Act high-risk point 3(b) | Watch |
| Any use outside class (research, datathon results) | — | Needs consent. Below 14, consent comes from parents | Needs consent |

Verdicts: **Good** is better than the rules ask. **OK** is covered by the educational function, or needed to run the app. **Reduce** means keep less of it. **Drop** means stop collecting it. **Watch** means fine today, but check again if the feature changes. **Needs consent** means only with consent.

## What is missing to be compliant

- **Information notice.** The student app shows no notice of what is recorded. Students and families must be told, in plain language, before the first use: what is saved, who sees it, for how long, and their rights.
- **Data to cut.** The table rates the full chat text Reduce and the page-switch events (`page_hidden`/`page_visible`) Drop.
- **Retention.** Nothing is ever deleted automatically. On the board, this covers the archive (the teacher can clear it by hand) and the progress files. On the laptop, it covers the [teacher store](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md) and the copies of the session files in its `raw/` folder. A school would set a limit (for example, the end of the school year) and delete after it.
- **Real erasure and access.** Deleting a student in the teacher app keeps their sessions as unassigned. Their code still appears in them and in the copies, so the data is not gone. A student's access request needs an export of their data.
- **Security.**
    - The teacher store is a plain SQLite file. It should sit on a school-managed, encrypted laptop, not a personal one.
    - On the board, anyone with a USB cable can read the session files: `adb` (the USB tool that the teacher app uses) needs no password. Physical access means full access.
    - The Wi-Fi password is printed on the [sticker](https://github.com/Sigkaio636/Santolina_tutor/blob/main/GLOSSARY.md). That is acceptable only because the student code is still needed to log in.
- **Impact assessment.** Systematic monitoring of minors with an AI tool is a typical case for a DPIA (data protection impact assessment). See the Departament's guide above. The school would run one before deploying.
- **The datathon itself.** Real student data could not be used for the datathon without consent. Synthetic data, as in the teacher app's demo (`teacher_app/simulate.py`), avoids the problem.

## Strengths worth keeping

- **Nothing leaves the board or the laptop:** no cloud, no third-party provider, so no processor contract and no data sent abroad.

## Sources

- [LOE, consolidated text (BOE)](https://www.boe.es/buscar/act.php?id=BOE-A-2006-7899): additional provision 23
- [AEPD, *Guía para centros educativos*](https://www.aepd.es/guias/guia-centros-educativos.pdf)
- [AEPD FAQ, *Menores y educación*](https://www.aepd.es/preguntas-frecuentes/10-menores-y-educacion)
- [APDCAT website](https://www.apdcat.cat): data protection guidelines for schools
- [Departament d'Educació, *Protecció de dades personals*](https://documents.espai.educacio.gencat.cat/IPCNormativa/DOIGC/GEST_Proteccio_dades.pdf)
- [EU AI Act, Annex III](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3)
