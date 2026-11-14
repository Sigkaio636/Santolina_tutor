# Student data: what a teacher may collect

Santolina is a proof of concept and will not be used with real students. This page asks a "what if": if a school in Catalonia used it, what could the teacher legally collect, and how does that compare with what the app collects today?

!!! warning "Not legal advice"
    This is a reading of the main texts by a datathon team, made in November 2026. A real deployment needs the school's data protection officer.

## The rules that apply

**GDPR** (EU Regulation 2016/679) applies to any personal data. A student code is still personal data: the teacher's laptop links it to a name, so the data is pseudonymised, not anonymous.

**Spanish Education Act (LOE), additional provision 23**, "Datos personales de los alumnos" ([consolidated text, BOE](https://www.boe.es/buscar/act.php?id=BOE-A-2006-7899)). It is the key text for schools:

- Schools may collect the student data "necesarios para el ejercicio de su función educativa". The text lists: family and social background, personal characteristics, "desarrollo y resultados de su escolarización", and other circumstances needed to teach and guide students (apartado 1).
- Enrolment implies this processing. The data must be "la estrictamente necesaria para la función docente y orientadora" and cannot be used "con fines diferentes del educativo sin consentimiento expreso" (apartado 2).
- Staff with access are bound by secrecy, and the school must apply security measures (apartado 3).

**Spanish Data Protection Act (LOPDGDD, Organic Law 3/2018).** Article 7 sets the age of consent at 14: below 14, consent comes from parents or guardians. Article 83 recognises the right to digital education ([AEPD FAQ on minors and education](https://www.aepd.es/preguntas-frecuentes/10-menores-y-educacion)).

**The Spanish Data Protection Agency's guide for schools** ([AEPD, *Guía para centros educativos*](https://www.aepd.es/guias/guia-centros-educativos.pdf)):

- "Por regla general, los centros educativos no necesitan el consentimiento" for the educational function.
- Schools must always **inform** families and students, clearly. Consent is needed only for purposes beyond education, explained one by one.
- Schools must know an app's privacy policy and conditions **before** using it, and reject apps that don't offer enough guarantees. A provider that handles data for the school is a processor and needs a contract.
- Data is kept only as long as needed for its purpose.

**The Catalan Data Protection Authority (APDCAT)** oversees Catalan public schools. It has published [data protection guidelines for schools](https://apdcat.gencat.cat/en/documentacio/guies_basiques/Guies-apdcat/Pautes-de-proteccio-de-dades-per-als-centres-educatius). The Departament d'Educació's [own guide](https://documents.espai.educacio.gencat.cat/IPCNormativa/DOIGC/GEST_Proteccio_dades.pdf) notes that some processing needs a **data protection impact assessment**.

**EU AI Act** (Regulation 2024/1689), [Annex III, point 3](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3):

- AI systems used to **evaluate learning outcomes, including when those outcomes steer the learning process** of students, are **high-risk**. So are systems that monitor students during tests.
- Article 5(1)(f) **bans emotion recognition** in education, except for medical or safety reasons.
- When the high-risk obligations start was being postponed in 2026, so check the current date before relying on it.

### What follows for a teacher

1. **The school decides, not the teacher alone.** The school (or the Departament, for public schools) is the controller. It must approve the tool before use.
2. **No consent is needed for learning data used to teach**: answers, results, progress, difficulties. Families and students must still be told what is collected and why.
3. **Consent is needed for anything else**: research, a datathon analysis, publishing results, showing a student's work outside class. Below 14, the consent comes from parents or guardians.
4. **Only what is strictly necessary**, kept only as long as needed, kept secure, with no other use.
5. **Adaptive AI is regulated.** A copilot that judges answers and chooses the next problem is close to Annex III 3(b). Emotion or attention inference is banned.

## What Santolina collects, compared

| What we collect | Today | Legal reading | Verdict |
| --- | --- | --- | --- |
| Name, group, notes (teacher's laptop only) | Yes | Basic school data, covered by the educational function | OK |
| Pseudonymous student code on the board, never the name | Yes | Good practice: the board holds no names | Good |
| Answers, right/wrong, attempt number, time per exercise | Yes | "Desarrollo y resultados de su escolarización": core educational data | OK |
| Clues used, solution shown, exercises left unsolved | Yes | Shows where a student struggles: needed for "orientación" | OK |
| Free-form questions to the copilot, and its replies (full text) | Yes | Useful to see doubts, but a child may write anything, including personal or health information. Not strictly necessary in full | Reduce |
| Leaving the page for another app (`page_hidden`/`page_visible`, seconds away) | Yes | Behavioural monitoring of attention. Hard to call "strictly necessary", and it points towards the attention inference the AI Act distrusts | Drop |
| Photos sent with a question | Size and type only, image not stored | Data minimisation done right | Good |
| Phone's clock at login | Yes | Technical, needed to date sessions | OK |
| IP address, device model, location | No (the demo server prints IPs to its log, only on the laptop) | — | Good |
| Learning path that picks an easier problem after a failure | Stub | Steering learning from evaluated outcomes: close to AI Act high-risk 3(b) once a real model drives it | Watch |
| Any use outside class (research, datathon results) | — | Needs consent; below 14, from parents | Needs consent |

## What is missing to be compliant

- **Information notice.** The student app shows no notice of what is recorded. Students and families must be told, in plain language, before the first use: what is saved, who sees it, for how long, and their rights.
- **Retention.** Nothing is ever deleted automatically: not the board's archive, and not the teacher's store. A school would set a limit (for example, the end of the school year) and delete after it.
- **Real erasure and access.** Deleting a student in the teacher app keeps their sessions as unassigned. Their code still appears in them, so the data is not gone. A student's access request needs an export of their data.
- **Security.**
    - The teacher's database is a plain SQLite file. It should sit on a school-managed, encrypted laptop, not a personal one.
    - On the board, anyone with a USB cable can read the session files: `adb` needs no password. Physical access means full access.
    - The Wi-Fi password is printed on the sticker. That is acceptable only because the code is still needed to log in.
- **Impact assessment.** Systematic monitoring of minors with an AI tool is a typical case where the school would run a DPIA before deploying.
- **The datathon itself.** Real student data could not be used for the datathon without consent. Synthetic data, as in the demo, avoids the problem.

## Strengths worth keeping

- **Nothing leaves the board or the laptop:** no cloud, no third-party provider, so no processor contract and no international transfer.
- **The board only knows codes.** Names live on the teacher's laptop.
- **Photos are not kept.**
- **The correct answer never reaches the phone.** That protects the exercise, not personal data, but it shows the habit of sending only what is needed.

## Sources

- [LOE, consolidated text (BOE)](https://www.boe.es/buscar/act.php?id=BOE-A-2006-7899): additional provision 23
- [AEPD, *Guía para centros educativos*](https://www.aepd.es/guias/guia-centros-educativos.pdf)
- [AEPD, *Orientaciones sobre apps y datos de alumnos*](https://www.aepd.es/guias/guia-orientaciones-apps-datos-alumnos.pdf)
- [AEPD FAQ, *Menores y educación*](https://www.aepd.es/preguntas-frecuentes/10-menores-y-educacion)
- [APDCAT, data protection guidelines for schools](https://apdcat.gencat.cat/en/documentacio/guies_basiques/Guies-apdcat/Pautes-de-proteccio-de-dades-per-als-centres-educatius)
- [Departament d'Educació, *Protecció de dades personals*](https://documents.espai.educacio.gencat.cat/IPCNormativa/DOIGC/GEST_Proteccio_dades.pdf)
- [EU AI Act, Annex III](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3)
