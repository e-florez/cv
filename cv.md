---
title: "Edison Flórez, Ph.D."
author: "Edison Flórez"
job: default        # change to 'data-science', 'academia', etc.
geometry: margin=1.6cm
fontsize: 11pt
colorlinks: true
lang: en
---

# Edison Flórez, Ph.D.  
*Data Scientist | Business Analyst | Computational Physicist*  

edisonffh@gmail.com • <https://github.com/e-florez> • <https://linkedin.com/in/edisonflorez>

---

## Profile
8 + years’ experience in statistical analysis, predictive modelling, data processing and mining algorithms across biotech and finance. I translate complex business requirements into scalable, data-driven solutions.

## Interests
Scientific computing · Data engineering · Machine learning for life-sciences · Data-driven storytelling

## Technical skills
Python · C/C++ · Fortran · SQL · MongoDB · Git · Docker · AWS · Power BI · Excel · Linux · Bash  

## General skills
Storytelling · Leadership · Project management · Data visualisation · Agile · Data preparation · DB design · Coaching & mentoring

---

## Professional experience

::: if (job == "business" or job == "default")
### Sales Executive & Business Analyst  
*Cordis, New Zealand* | Sep 2023 – Present  
• Managed key corporate accounts, nurturing relationships through site inspections and on-site hosting.  
• Queried Delphi CRM, Oracle PMS & GDS databases to surface booking-trend insights.  
• Built Python ETL pipelines and interactive dashboards → **35 %** reduction in manual reporting time.  

**Achievement:** beat monthly sales target, driving an **8 %** rise in corporate-segment revenue.
:::

::: if (job == "data-science" or job == "default")
### Data Scientist  
*HelicoBio, New Zealand* | Aug 2021 – Aug 2023  
• Designed and validated scalable data pipelines (Python & C++) to accelerate plant-biology research.  
• Collaborated cross-functionally to deploy new functionality end-to-end.  

**Achievement:** reduced wet-lab workflows by **20 %**, improving protein-design throughput.
:::

::: if (job == "editorial" or job == "default")
### Freelance Scientific Editor  
*Enago* (Apr 2023 – Present) · *MDPI* (Apr 2018 – Dec 2018)  
Copy- & substantive-editing for STEM manuscripts; guidance on journal style compliance.  

**Achievement:** boosted desk-acceptance rates by **30 %** in high-impact journals.
:::

::: if (job == "academia" or job == "default")
### Lab Assistant & Demonstrator  
*Massey University, NZ* | Aug 2018 – Mar 2020  
Taught mechanics, thermodynamics, E&M and circuits; authored SOPs and automated reports with Jupyter/Pandas.  
:::

::: if (job == "consulting" or job == "default")
### Data Scientist  
*EY, Colombia* | Aug 2016 – Mar 2018  
Developed SAP Analytical Banking/BI models; built Python encryption module that halved training-prep time.  
:::

### Graduate Teaching Assistant  
*University of Antioquia, CO* | Sep 2015 – Aug 2016  
Created “Computational Quantum Mechanics with Python” module adopted in Quantum Chemistry curriculum.

---

## Open-source contributions
**PTMC** – Parallel Tempering Monte Carlo code (Fortran) • Lead developer  
<https://github.com/e-florez/PTMC>  

**AMCESS** – Potential-energy-surface explorer (Python) • Architect  
<https://github.com/e-florez/amcess>

---

::: if (job == "academia" or job == "default")
## Selected publications
1. *The Journal of Physical Chemistry A* **127** (2023) 8032–8049. DOI 10.1021/acs.jpca.3c02927 – front-cover article.  
2. *J. Chem. Phys.* **157** (2022) 064304. DOI 10.1063/5.0097642  
3. *Int. J. Quantum Chem.* **121** (2021) e26571.  
4. Additional list available on request.
:::

---

## Education
* Ph.D. Computational Physics – Massey University, NZ (Jul 2023)  
* M.Sc. Computational Chemistry – University of Antioquia, CO (Dec 2014)  
* B.Sc. Chemistry – University of Antioquia, CO (Jul 2012)  

---

## Fellowships & awards
Massey University Doctoral Scholarship · M.Sc. Honours (meritorious research)

---

## Supervision
M.Sc. thesis (Feb 2020) – “Microsolvation of Heavy Halides”  
B.Sc. thesis (Dec 2017) – “Relativistic & Correlation Effects on NMR of MX Diatomics”

---

## References
Available upon request

---

_Yours sincerely_  
**Edison Flórez, Ph.D.**  
edisonffh@gmail.com

---

## 🔧 Build & automation (maintainer notes)

> The following steps implement the **Pandoc Markdown-first workflow** that
> generates synced PDFs and this README.

### 1  Edit
Update only this file (`cv.md`). Use fenced *conditional* blocks (`::: if …`) to control which sections appear in job-specific variants.

### 2  Build locally
```bash
pandoc cv.md -o Edison_Florez_CV.pdf                       # default
pandoc cv.md -M job=data-science   -o Edison_Florez_DS.pdf # data-science
pandoc cv.md -M job=academia       -o Edison_Florez_AC.pdf # academia