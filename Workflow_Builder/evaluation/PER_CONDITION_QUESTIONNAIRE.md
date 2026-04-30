# Per-condition Questionnaire

Complete this questionnaire **after each condition** (Python / Workflow Builder). Each participant fills it in twice in total — once after the Python condition and once after the Workflow Builder condition.

It combines two standard usability instruments:

- **Section A — System Usability Scale (SUS).** A ten-item Likert questionnaire that yields a single 0–100 usability score per condition.
- **Section B — NASA Task Load Index (raw TLX).** Six 1–21 scales covering perceived workload across mental, physical, temporal, performance, effort, and frustration dimensions.

---

## Section A: System Usability Scale (SUS)

**Condition:** ☐ Python &nbsp;&nbsp; ☐ Workflow Builder

For each statement, circle a number from 1 (Strongly Disagree) to 5 (Strongly Agree).

| # | Statement | Strongly Disagree | | | | Strongly Agree |
|---|-----------|:-:|:-:|:-:|:-:|:-:|
| 1 | I think that I would like to use this system frequently. | 1 | 2 | 3 | 4 | 5 |
| 2 | I found the system unnecessarily complex. | 1 | 2 | 3 | 4 | 5 |
| 3 | I thought the system was easy to use. | 1 | 2 | 3 | 4 | 5 |
| 4 | I think that I would need the support of a technical person to be able to use this system. | 1 | 2 | 3 | 4 | 5 |
| 5 | I found the various functions in this system were well integrated. | 1 | 2 | 3 | 4 | 5 |
| 6 | I thought there was too much inconsistency in this system. | 1 | 2 | 3 | 4 | 5 |
| 7 | I would imagine that most people would learn to use this system very quickly. | 1 | 2 | 3 | 4 | 5 |
| 8 | I found the system very cumbersome to use. | 1 | 2 | 3 | 4 | 5 |
| 9 | I felt very confident using the system. | 1 | 2 | 3 | 4 | 5 |
| 10 | I needed to learn a lot of things before I could get going with this system. | 1 | 2 | 3 | 4 | 5 |

---

## Section B: NASA Task Load Index (Raw TLX)

**Condition:** ☐ Python &nbsp;&nbsp; ☐ Workflow Builder

For each dimension, mark a point on the scale from 1 to 21.

### Mental Demand
*How mentally demanding was the task?*

```
Very Low  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Very High
```


### Physical Demand
*How physically demanding was the task?*

```
Very Low  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Very High
```


### Temporal Demand
*How hurried or rushed was the pace of the task?*

```
Very Low  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Very High
```


### Performance
*How successful were you in accomplishing what you were asked to do?*

```
Perfect  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Failure
```


### Effort
*How hard did you have to work to accomplish your level of performance?*

```
Very Low  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Very High
```


### Frustration
*How insecure, discouraged, irritated, stressed, and annoyed were you?*

```
Very Low  1---2---3---4---5---6---7---8---9---10---11---12---13---14---15---16---17---18---19---20---21  Very High
```


---

## Scoring Reference (for facilitator use only)

### SUS Scoring
1. For odd-numbered items (1, 3, 5, 7, 9): adjusted score = raw score − 1
2. For even-numbered items (2, 4, 6, 8, 10): adjusted score = 5 − raw score
3. Sum all 10 adjusted scores
4. Multiply by 2.5

**Result:** SUS score from 0–100

| Score | Grade | Interpretation |
|-------|-------|----------------|
| > 85 | A | Excellent |
| 73–85 | B | Good |
| 52–73 | C | OK / Above Average |
| < 52 | D/F | Below Average / Poor |

### NASA-TLX Scoring
Raw TLX: simply average the 6 dimension scores (no weighting needed).
Lower scores = less workload (except Performance, where lower = better performance).
