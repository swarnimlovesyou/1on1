"""Logical reasoning guides for the reasoning track (Prep). Checked by check_prep.py."""

SYLLOGISM_OPTIONS = ['Only I follows', 'Only II follows', 'Both follow', 'Neither follows']

GUIDES = [
    dict(
        id='guide-reasoning-number-series', kind='guide', track='reasoning', drill='number-series',
        title='Number series', order=1,
        summary="Every number series hides one rule that turns each term into the next, and a fixed order of checks finds it quickly.",
        sections=[
            dict(title='Start with the differences', text=(
                "A number series hides one rule that turns each term into the next. Your first move is almost always to write the differences between neighbouring terms underneath the series. "
                "If the differences are all equal, the series is arithmetic: 7, 12, 17, 22 adds 5 each time, so the next term is 27.\n\n"
                "If the differences are not equal, treat them as a new series. When the differences themselves grow by a fixed amount, you are looking at differences of differences. "
                "For 2, 3, 6, 11, 18 the differences are 1, 3, 5, 7, which rise by 2, so the next difference is 9 and the next term is 27.\n\n"
                "If the terms grow fast and the differences roughly double or triple, try ratios instead. Dividing each term by the one before it reveals a geometric series: 3, 12, 48, 192 multiplies by 4 each time, so 768 comes next.\n\n"
                "Work in a fixed order: differences, ratios, known squares and cubes, then alternating patterns. Most series give way at one of these steps in under a minute."
            )),
            dict(title='Squares, cubes and a constant', text=(
                "Some series are built from perfect squares or cubes with a small number added or taken away. Knowing the squares up to 30 and the cubes up to 15 by heart lets you spot them on sight.\n\n"
                "Take 3, 6, 11, 18, 27. The differences 3, 5, 7, 9 are consecutive odd numbers, which is the fingerprint of squares. "
                "Subtract 2 from each term and you get 1, 4, 9, 16, 25, so the rule is n squared plus 2 and the next term is 36 + 2 = 38.\n\n"
                "For cubes, compare each term with 1, 8, 27, 64, 125. The series 4, 11, 30, 67, 128 is each cube plus 3, so 216 + 3 = 219 comes next.\n\n"
                "Watch for multiply-then-add rules as well. In 2, 5, 11, 23, 47 every term is double the previous one plus 1. "
                "The differences 3, 6, 12, 24 double each time, and that doubling is the clue that a multiply step is involved, so the next term is 95."
            )),
            dict(title='Alternating and interleaved series', text=(
                "When the differences jump up and down with no steady trend, suspect two rules taking turns. There are two common shapes.\n\n"
                "In the first, one series uses two operations in turn. The series 6, 10, 9, 13, 12, 16 goes add 4, subtract 1, add 4, subtract 1, add 4, so the next step is subtract 1, giving 15.\n\n"
                "In the second, two separate series are woven together. Read the odd positions and the even positions as two different lists. "
                "In 1, 20, 3, 17, 5, 14, 7 the odd positions 1, 3, 5, 7 climb by 2, while the even positions 20, 17, 14 fall by 3. "
                "The missing eighth term sits in an even position, so it is 14 - 3 = 11.\n\n"
                "The tell-tale sign of interleaving is that terms two places apart look more related than neighbours do. "
                "Long series of seven or more terms often hide two lists. Before applying any rule, always check which position the missing term occupies."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Find the next term: 5, 10, 8, 16, 14, 28, ?\n\n"
                "Step 1: differences are +5, -2, +8, -2, +14. They do not settle, but every second step is -2, so suspect two alternating operations. "
                "Step 2: test multiply by 2 for the other steps: 5 x 2 = 10, 8 x 2 = 16, 14 x 2 = 28. All match. "
                "Step 3: the rule is x2, then -2, repeating. The last step was x2 (14 to 28), so the next is -2: 28 - 2 = 26. Answer: 26.\n\n"
                "Example 2. Find the next term: 1, 3, 8, 18, 35, ?\n\n"
                "Step 1: differences are 2, 5, 10, 17. Not constant. "
                "Step 2: differences of those are 3, 5, 7, rising by 2, so the next second difference is 9. "
                "Step 3: the next first difference is 17 + 9 = 26. "
                "Step 4: the next term is 35 + 26 = 61. "
                "Check another way: the differences 2, 5, 10, 17 are 1, 4, 9, 16 each plus 1, and the next square plus 1 is 25 + 1 = 26, which agrees. Answer: 61."
            )),
        ],
        keyPoints=[
            'Write the differences first; equal differences mean an arithmetic series.',
            'If the differences grow by a fixed amount, take differences of differences.',
            'Fast growth suggests ratios or a multiply-then-add rule.',
            'Consecutive odd differences are the fingerprint of squares; compare terms with known squares and cubes.',
            'If terms two places apart look related, split the series into odd and even positions.',
        ],
        challenges=[
            dict(id='challenge-reasoning-number-series-q1', kind='prediction', title='Growing gaps',
                 prompt="What comes next? 4, 11, 25, 46, 74, ?",
                 options=['102', '109', '111', '116'], answer=1,
                 explanation="The differences are 7, 14, 21, 28, which are multiples of 7 rising by 7 each time. The next difference is 35, so 74 + 35 = 109. 102 comes from repeating the last difference of 28, which ignores that the gaps keep growing.",
                 hint='Write the gaps between neighbouring terms and look at what they have in common.'),
            dict(id='challenge-reasoning-number-series-q2', kind='prediction', title='Fast climber',
                 prompt="What comes next? 7, 21, 63, 189, ?",
                 options=['315', '378', '945', '567'], answer=3,
                 explanation="Each term is three times the previous one: 7 x 3 = 21, 21 x 3 = 63, 63 x 3 = 189, so 189 x 3 = 567. 315 comes from adding the last difference again (189 + 126), which treats a geometric series as if it were arithmetic.",
                 hint='The terms grow quickly. Try dividing instead of subtracting.'),
            dict(id='challenge-reasoning-number-series-q3', kind='prediction', title='Hidden squares',
                 prompt="What comes next? 6, 11, 18, 27, 38, ?",
                 options=['51', '49', '50', '53'], answer=0,
                 explanation="The differences 5, 7, 9, 11 are consecutive odd numbers, a sign of squares. Each term is a square plus 2: 4 + 2, 9 + 2, 16 + 2, 25 + 2, 36 + 2. The next is 49 + 2 = 51. Equally, the next difference is 13 and 38 + 13 = 51. Picking 49 means spotting the squares but forgetting the constant added to each.",
                 hint='Compare each term with a perfect square close to it.'),
            dict(id='challenge-reasoning-number-series-q4', kind='prediction', title='Two steps in turn',
                 prompt="What comes next? 3, 8, 6, 11, 9, 14, ?",
                 options=['17', '19', '12', '11'], answer=2,
                 explanation="The steps go +5, -2, +5, -2, +5, so the next step is -2: 14 - 2 = 12. Reading odd positions (3, 6, 9, 12) confirms it. 17 comes from adding 3 to 14, which mixes up the two interleaved lists: the even positions 8, 11, 14 rise by 3, but the missing term is in an odd position.",
                 hint='Look at the signs of the differences and at which position the missing term occupies.'),
            dict(id='challenge-reasoning-number-series-q5', kind='prediction', title='Close to cubes',
                 prompt="What comes next? 6, 25, 62, 123, 214, ?",
                 options=['305', '343', '345', '341'], answer=3,
                 explanation="Compare with the cubes 8, 27, 64, 125, 216: every term is two less, so the rule is n cubed minus 2, starting from n = 2. The next cube is 7 x 7 x 7 = 343, so the next term is 343 - 2 = 341. 343 is the cube itself with the constant forgotten, 345 adds 2 instead of taking it away, and 305 repeats the last difference of 91 instead of noticing the differences grow.",
                 hint='Each term sits right next to a well-known power.'),
        ],
    ),
    dict(
        id='guide-reasoning-letter-series', kind='guide', track='reasoning', drill='letter-series',
        title='Letter series', order=2,
        summary="Turn letters into their alphabet positions, find the numeric rule, and wrap round from Z to A when a step runs off the end.",
        sections=[
            dict(title='Turn letters into numbers', text=(
                "Letter series become number series once you swap each letter for its position: A = 1, B = 2, and so on up to Z = 26. "
                "The whole skill is doing that conversion fast and without slips.\n\n"
                "Learn a few anchors rather than counting from A every time. A handy set is E = 5, J = 10, O = 15, T = 20, Y = 25. "
                "To find R, start from T = 20 and step back two: R = 18. To find L, start from J = 10 and step forward two: L = 12.\n\n"
                "Reverse positions count from the Z end, so Z is 1st from the right and A is 26th. "
                "A letter's forward position and reverse position always add up to 27. So the 6th letter from the right is the 27 - 6 = 21st letter from the left, which is U.\n\n"
                "The same 27 rule pairs each letter with its opposite: A and Z, B and Y, C and X, through to M and N. These opposite pairs turn up constantly in series and in codes."
            )),
            dict(title='Fixed steps and wrapping round', text=(
                "Once letters are numbers, look at the steps between them. A fixed step works just like an arithmetic number series. "
                "C, F, I, L adds 3 each time, so the next letter is position 15, which is O.\n\n"
                "The twist is that the alphabet has only 26 letters. If a step takes you past Z, subtract 26 to wrap round to the start. "
                "W (23) plus 5 is 28, and 28 - 26 = 2, which is B. If a backward step takes you below A, add 26. "
                "C (3) minus 5 is -2, and -2 + 26 = 24, which is X.\n\n"
                "Picture the alphabet as a circle rather than a line and wrap-around stops feeling like a special case.\n\n"
                "Backward series work the same way with negative steps. Z, W, T, Q steps back by 3, so N comes next. "
                "If the steps are not fixed, apply every number-series idea you know to the list of steps: they may grow by 1 each time, alternate, or double."
            )),
            dict(title='Changing gaps and paired letters', text=(
                "Many letter series use gaps that grow. A, C, F, J uses gaps of 2, 3, 4, so the next gap is 5 and the next letter is position 15, O. "
                "Writing the gaps under the series makes this obvious at a glance.\n\n"
                "Series of letter groups, such as AZ, BY, CX, look harder but are really two or more simple series side by side. "
                "Treat the first letters as one list and the second letters as another. Here the first letters go A, B, C and the second letters go Z, Y, X, so the next group is DW.\n\n"
                "Each position in a group can follow its own step. In KP, MN, OL, the first letters rise by 2 (K, M, O, Q) while the second letters fall by 2 (P, N, L, J), so QJ comes next.\n\n"
                "Before settling on an answer, check whether the letters in each group are linked to each other as well, for example as opposite pairs. "
                "A second relationship that agrees is a good sign you have the rule right."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Find the next letter: J, M, Q, V, ?\n\n"
                "Step 1: convert to positions: J = 10, M = 13, Q = 17, V = 22. "
                "Step 2: gaps are 3, 4, 5, growing by 1, so the next gap is 6. "
                "Step 3: 22 + 6 = 28, which is past Z. "
                "Step 4: wrap round: 28 - 26 = 2, which is B. Answer: B.\n\n"
                "Example 2. Find the next group: BY, DW, FU, HS, ?\n\n"
                "Step 1: first letters B, D, F, H are positions 2, 4, 6, 8, rising by 2, so the next first letter is 10, which is J. "
                "Step 2: second letters Y, W, U, S are positions 25, 23, 21, 19, falling by 2, so the next second letter is 17, which is Q. "
                "Step 3: check with the 27 rule: 2 + 25, 4 + 23, 6 + 21 and 8 + 19 all make 27, so each pair is a letter and its opposite. "
                "The opposite of J (10) is 27 - 10 = 17, which is Q, so both routes agree. Answer: JQ."
            )),
        ],
        keyPoints=[
            'Convert letters to positions A = 1 to Z = 26; anchors E, J, O, T, Y are 5, 10, 15, 20, 25.',
            'Forward and reverse positions of a letter add up to 27, and so do opposite letters such as A and Z.',
            'Past Z, subtract 26; below A, add 26.',
            'Write the gaps under the series and treat them like a number series.',
            'Split letter groups into separate series, one per position.',
        ],
        challenges=[
            dict(id='challenge-reasoning-letter-series-q1', kind='prediction', title='From the far end',
                 prompt="Which letter is 8th from the right end of the English alphabet?",
                 options=['R', 'S', 'T', 'H'], answer=1,
                 explanation="A letter's position from the left and from the right add up to 27, so 8th from the right is 27 - 8 = 19th from the left, which is S. R comes from computing 26 - 8 = 18, which is off by one because Z itself is counted as 1st from the right.",
                 hint='Counting from the right and counting from the left are linked by a fixed total.'),
            dict(id='challenge-reasoning-letter-series-q2', kind='prediction', title='Stepping back',
                 prompt="What comes next? Y, U, Q, M, ?",
                 options=['J', 'H', 'I', 'K'], answer=2,
                 explanation="Positions are 25, 21, 17, 13, falling by 4 each time. 13 - 4 = 9, which is I. J would be a fall of only 3, and H a fall of 5.",
                 hint='Convert each letter to its position and look at the gaps.'),
            dict(id='challenge-reasoning-letter-series-q3', kind='prediction', title='Round the corner',
                 prompt="What comes next? R, W, B, G, ?",
                 options=['L', 'K', 'M', 'Q'], answer=0,
                 explanation="R = 18 and W = 23 is a step of 5. 23 + 5 = 28, and wrapping round gives 28 - 26 = 2, which is B, so the series continues past Z. G = 7, and 7 + 5 = 12, which is L. K comes from miscounting the step as 4 after the wrap; the step stays 5 throughout.",
                 hint='Think of the alphabet as a circle, not a line.'),
            dict(id='challenge-reasoning-letter-series-q4', kind='prediction', title='Pairs with different steps',
                 prompt="What comes next? AC, BE, CG, DI, ?",
                 options=['EJ', 'FK', 'EL', 'EK'], answer=3,
                 explanation="First letters A, B, C, D rise by 1, so the next is E. Second letters C, E, G, I are 3, 5, 7, 9, rising by 2, so the next is 11, which is K. The answer is EK. EJ uses a step of 1 for the second letter too, but the second letters clearly skip one each time.",
                 hint='Treat the first letters and the second letters as two separate series.'),
            dict(id='challenge-reasoning-letter-series-q5', kind='prediction', title='Widening gaps',
                 prompt="What comes next? C, D, F, I, M, ?",
                 options=['Q', 'R', 'S', 'P'], answer=1,
                 explanation="Positions are 3, 4, 6, 9, 13, so the gaps are 1, 2, 3, 4. The next gap is 5, and 13 + 5 = 18, which is R. Q comes from repeating the last gap of 4 instead of letting it grow.",
                 hint='Write down the gaps and see how they change.'),
        ],
    ),
    dict(
        id='guide-reasoning-coding-decoding', kind='guide', track='reasoning', drill='coding-decoding',
        title='Coding and decoding', order=3,
        summary="Work out the rule that turns a sample word into its code by comparing letter positions, then apply it forwards to code or backwards to decode.",
        sections=[
            dict(title='Find the rule from a known pair', text=(
                "A coding question gives you a word and its code, then asks you to code or decode something new. The method is always the same: write the positions of the plain word and the code word one above the other, and look at how each letter moved.\n\n"
                "For each pair of letters, work out code position minus plain position. If every letter moved by the same amount, you have a shift code. "
                "A move that looks far out of line, such as Y to A giving -24, is usually a wrap round the alphabet: add or subtract 26, so -24 is really +2. "
                "If the amounts still differ, check whether each pair adds up to 27, which marks a reverse-alphabet code. "
                "If neither fits, look for a step that changes with the letter's place in the word, such as +1 for the first letter, +2 for the second and so on, or for a word that has simply been written backwards.\n\n"
                "Test the rule on every letter of the example, not just the first one or two. A rule that fits two letters by luck will give a wrong answer.\n\n"
                "When a question gives more than one example, use them all, because a second example often rules out a rival rule that fits the first."
            )),
            dict(title='Shift codes forwards and backwards', text=(
                "In a shift code every letter moves the same number of places along the alphabet. A forward shift of 1 turns A into B and CAT into DBU. A backward shift of 3 turns F into C.\n\n"
                "Wrap-around matters here exactly as in letter series. A forward shift of 2 turns Y (25) into 27, and 27 - 26 = 1, so Y becomes A. "
                "A backward shift of 3 turns B (2) into -1, and -1 + 26 = 25, so B becomes Y.\n\n"
                "Decoding means running the rule in reverse. If the code was made by shifting forward 2, you get the original by shifting the code letters back 2. "
                "Students often apply the coding rule again instead of undoing it, which shifts the letters twice as far from the answer.\n\n"
                "A quick sanity check: after decoding, the result should usually be a real word. If you get something unpronounceable, recheck the direction of the shift before anything else."
            )),
            dict(title='Reverse-alphabet and number codes', text=(
                "In a reverse-alphabet code each letter is swapped for its opposite: A with Z, B with Y, C with X, and so on. "
                "Since a letter and its opposite always add up to 27, the code for a letter at position p is the letter at 27 - p. "
                "The code works the same in both directions, so coding and decoding are the same operation.\n\n"
                "Number codes replace letters with numbers. The simplest writes each letter's position, so BAD becomes 2-1-4. "
                "Others combine the positions, for example by adding them: CAB would be 3 + 1 + 2 = 6.\n\n"
                "With combined codes, be wary of rival rules. CAB gives 6 whether you add the positions or multiply them, so one example cannot tell the two apart. "
                "A second example settles it: FED gives 6 + 5 + 4 = 15 by adding but 120 by multiplying. "
                "Always check your chosen rule against every example the question provides, and pick the one that fits them all."
            )),
            dict(title='Worked examples', text=(
                "Example 1. If LAMP is coded as NCOR, how is DESK coded?\n\n"
                "Step 1: positions of LAMP are 12, 1, 13, 16. Positions of NCOR are 14, 3, 15, 18. "
                "Step 2: each letter moved by +2, so this is a forward shift of 2. "
                "Step 3: DESK is 4, 5, 19, 11. Adding 2 gives 6, 7, 21, 13. "
                "Step 4: convert back: F, G, U, M. Answer: FGUM.\n\n"
                "Example 2. If PEN is coded as KVM, how is INK coded?\n\n"
                "Step 1: PEN is 16, 5, 14 and KVM is 11, 22, 13. "
                "Step 2: the moves are -5, +17, -1, which are not equal, so this is not a shift code. "
                "Step 3: try sums: 16 + 11 = 27, 5 + 22 = 27, 14 + 13 = 27. Every pair makes 27, so it is a reverse-alphabet code. "
                "Step 4: INK is 9, 14, 11. Opposites are 27 - 9 = 18, 27 - 14 = 13, 27 - 11 = 16. "
                "Step 5: convert back: R, M, P. Answer: RMP."
            )),
        ],
        keyPoints=[
            'Write plain and code positions one above the other and compare every letter.',
            'Equal moves mean a shift code; pairs adding up to 27 mean a reverse-alphabet code.',
            'Wrap round past Z or below A when shifting.',
            'Decode by undoing the rule, not by applying it again.',
            'With number codes, use every example to rule out rival rules.',
        ],
        challenges=[
            dict(id='challenge-reasoning-coding-decoding-q1', kind='prediction', title='One step forward',
                 prompt="If BOOK is coded as CPPL, how is DESK coded?",
                 options=['EFTL', 'CDRJ', 'EFTM', 'FGUM'], answer=0,
                 explanation="B to C, O to P, O to P and K to L are each a move of +1. Applying +1 to DESK gives D to E, E to F, S to T and K to L: EFTL. CDRJ shifts the wrong way (-1), and FGUM shifts by 2.",
                 hint='Compare each letter of BOOK with the letter below it in CPPL.'),
            dict(id='challenge-reasoning-coding-decoding-q2', kind='prediction', title='Backwards with a wrap',
                 prompt="If MILK is coded as KGJI, how is SOAP coded?",
                 options=['QMZN', 'UQCR', 'QMYN', 'QNYM'], answer=2,
                 explanation="M to K, I to G, L to J and K to I are each a move of -2. For SOAP: S (19) to 17 = Q, O (15) to 13 = M, A (1) to -1, which wraps to -1 + 26 = 25 = Y, and P (16) to 14 = N. The code is QMYN. QMZN moves A back by only 1, and UQCR shifts forward instead of back.",
                 hint='Work out the shift from MILK, then take extra care with the letter at the start of the alphabet.'),
            dict(id='challenge-reasoning-coding-decoding-q3', kind='prediction', title='Mirror alphabet',
                 prompt="If GOLD is written as TLOW, how is SILVER written?",
                 options=['HRPEVI', 'IVEORH', 'HROFVI', 'HROEVI'], answer=3,
                 explanation="G (7) and T (20), O (15) and L (12), L (12) and O (15), D (4) and W (23) each add up to 27, so every letter is replaced by its opposite. SILVER is 19, 9, 12, 22, 5, 18, whose opposites are 8, 18, 15, 5, 22, 9: H, R, O, E, V, I, giving HROEVI. IVEORH has the right letters but reverses their order, which this code does not do.",
                 hint='The moves from GOLD to TLOW are not all equal, so this is not a shift. Look for another fixed link between each pair of letters.'),
            dict(id='challenge-reasoning-coding-decoding-q4', kind='prediction', title='Letters to a number',
                 prompt="In a code, CAB = 6 and FED = 15. What is the code for HIGH?",
                 options=['24', '32', '34', '36'], answer=1,
                 explanation="Adding positions fits both examples: C + A + B = 3 + 1 + 2 = 6 and F + E + D = 6 + 5 + 4 = 15. Multiplying also gives 6 for CAB but 120 for FED, so it is ruled out. HIGH is 8 + 9 + 7 + 8 = 32. 24 counts the repeated H only once (8 + 9 + 7); every letter in the word counts, including repeats.",
                 hint='Find one rule that fits both examples, not just the first.'),
            dict(id='challenge-reasoning-coding-decoding-q5', kind='prediction', title='Undo the code',
                 prompt="In a code, every letter is replaced by the letter two places after it in the alphabet. A word is coded as GCUA. What is the original word?",
                 options=['IEWC', 'EAST', 'EASY', 'FBTZ'], answer=2,
                 explanation="To decode, move each letter two places back: G to E, C to A, U to S, and A (1) to -1, which wraps to 25 = Y. The word is EASY. IEWC applies the coding rule again instead of undoing it, and EAST guesses a familiar word: A moved back two places wraps round to Y, not T.",
                 hint='Decoding runs the rule in the opposite direction. Watch the last letter.'),
        ],
    ),
    dict(
        id='guide-reasoning-directions', kind='guide', track='reasoning', drill='directions',
        title='Direction sense', order=4,
        summary="Track a person's facing direction through each turn and their position on an x-y grid, then use Pythagoras for the straight-line distance.",
        sections=[
            dict(title='The compass and turning', text=(
                "Draw the compass the usual way: north at the top, south at the bottom, east to the right and west to the left. "
                "Halfway between them sit north-east, south-east, south-west and north-west.\n\n"
                "A turn is always relative to the way the person is currently facing, not to the page. A right turn is 90 degrees clockwise and a left turn is 90 degrees anticlockwise. "
                "Turning right repeatedly cycles north, east, south, west and back to north. Turning left cycles the other way.\n\n"
                "Shortcuts save time with long chains of turns. Two rights, or two lefts, make a U-turn. A right followed by a left cancels out. "
                "Four turns the same way bring you back to where you started facing. So count the rights, subtract the lefts, and only the remainder after dividing by 4 matters: a net of 3 rights is the same as 1 left, and a net of 2 either way is a U-turn.\n\n"
                "Degree turns follow the same idea. Give each direction a bearing measured clockwise from north (north 0, east 90, south 180, west 270), add for clockwise turns and subtract for anticlockwise ones, "
                "then add or subtract 360 until the total lies between 0 and 359. "
                "Starting from the same direction, a turn of 270 degrees anticlockwise ends up facing the same way as a turn of 90 degrees clockwise, because 360 - 270 = 90."
            )),
            dict(title='Tracking position with x and y', text=(
                "For any question about distance or position, put the starting point at (0, 0) on a grid. Moving east adds to x, west subtracts from x, north adds to y and south subtracts from y.\n\n"
                "Go through the walk one leg at a time. For each leg, first update the facing direction if there was a turn, then add the distance in that direction. "
                "Keep a small table of direction, distance and running position so that nothing gets lost.\n\n"
                "For example, walking 5 m north, then 7 m east, then 2 m south gives positions (0, 5), (7, 5) and (7, 3).\n\n"
                "Only the final x and y matter for the answer. The total distance walked, which here is 5 + 7 + 2 = 14 m, is almost never what the question asks for, yet it often appears among the options as a trap. "
                "The x-y method also handles legs that cancel: walking 6 m east and later 6 m west leaves x unchanged, however far apart those legs are in the walk."
            )),
            dict(title='Distance and direction from the start', text=(
                "Once you have the final position (x, y), the straight-line distance from the start is the square root of x squared plus y squared. This is Pythagoras: the east-west and north-south displacements are the two shorter sides of a right-angled triangle.\n\n"
                "Setters like whole-number answers, so learn the common triples: 3, 4, 5; 6, 8, 10; 5, 12, 13; 9, 12, 15; and 8, 15, 17. "
                "If your x and y match the first two numbers of a triple, the distance is the third.\n\n"
                "The direction of the final point from the start comes from the signs. Positive x and positive y is north-east, positive x and negative y is south-east, and so on. "
                "If x is 0, the point is due north or due south; if y is 0, it is due east or due west.\n\n"
                "Read the question carefully: the direction of the start from the person is the exact opposite. If the person is north-east of the start, the start is south-west of the person."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Asha faces north and walks 6 km, then turns left and walks 8 km. Where is she relative to the start, and which way does she face?\n\n"
                "Step 1: start at (0, 0); 6 km north reaches (0, 6). "
                "Step 2: left from north is west; 8 km west reaches (-8, 6). "
                "Step 3: distance is the square root of 64 + 36 = 100, which is 10 km. "
                "Step 4: x is negative and y is positive, so she is north-west of the start, and she is facing west.\n\n"
                "Example 2. Kabir faces east and walks 15 km, turns left for 2 km, turns left for 3 km, then turns right for 7 km. How far is he from the start, and which way does he face?\n\n"
                "Step 1: east 15 km: (15, 0). "
                "Step 2: left from east is north; 2 km: (15, 2). "
                "Step 3: left from north is west; 3 km: (12, 2). "
                "Step 4: right from west is north; 7 km: (12, 9). "
                "Step 5: distance is the square root of 144 + 81 = 225, which is 15 km, from the 9, 12, 15 triple. He faces north, and he is north-east of the start."
            )),
        ],
        keyPoints=[
            'Turns are relative to the current facing direction: right is clockwise, left is anticlockwise.',
            'Two same-way turns make a U-turn; a right and a left cancel.',
            'Put the start at (0, 0): east and north are positive, west and south negative.',
            'Straight-line distance is the square root of x squared plus y squared; know the common triples.',
            'The total path walked is rarely the answer.',
        ],
        challenges=[
            dict(id='challenge-reasoning-directions-q1', kind='prediction', title='Three turns',
                 prompt="Meera faces south. She turns right, then right again, then left. Which direction is she facing now?",
                 options=['East', 'North', 'West', 'South'], answer=2,
                 explanation="Right from south is west. Right from west is north. Left from north is west. She faces west. Equivalently, two rights and one left net to one right turn, and one right from south is west. East comes from turning the wrong way, treating right as anticlockwise.",
                 hint='Remember that right means clockwise from the way she is facing at that moment.'),
            dict(id='challenge-reasoning-directions-q2', kind='prediction', title='As the crow flies',
                 prompt="Dev walks 4 km north, turns left and walks 3 km. How far is he from his starting point in a straight line?",
                 options=['7 km', '5 km', '1 km', '6 km'], answer=1,
                 explanation="He ends at (-3, 4). The distance is the square root of 9 + 16 = 25, which is 5 km. 7 km is the total distance walked, not the straight-line distance.",
                 hint='The two legs are at right angles to each other.'),
            dict(id='challenge-reasoning-directions-q3', kind='prediction', title='Where did she end up',
                 prompt="Nisha walks 9 m east, turns right and walks 5 m, then turns right again and walks 13 m. In which direction is she from her starting point?",
                 options=['South-west', 'South-east', 'North-west', 'West'], answer=0,
                 explanation="East 9 m gives (9, 0). Right from east is south, so 5 m gives (9, -5). Right from south is west, so 13 m gives (-4, -5). x is negative and y is negative, so she is south-west of the start. South-east would be right only if the last leg were shorter than 9 m, but it overshoots the start by 4 m.",
                 hint='Track x and y separately, then look at their signs.'),
            dict(id='challenge-reasoning-directions-q4', kind='prediction', title='Net displacement',
                 prompt="Arjun walks 10 m north, turns right and walks 6 m, turns right and walks 18 m, then turns left and walks 9 m. How far is he from the start?",
                 options=['43 m', '23 m', '15 m', '17 m'], answer=3,
                 explanation="North 10 m: (0, 10). Right from north is east, 6 m: (6, 10). Right from east is south, 18 m: (6, -8). Left from south is east, 9 m: (15, -8). The distance is the square root of 225 + 64 = 289, which is 17 m. 43 m is the total distance walked, and 15 m is only the east-west part.",
                 hint='Combine all the east-west legs and all the north-south legs before using Pythagoras.'),
            dict(id='challenge-reasoning-directions-q5', kind='prediction', title='Turning by degrees',
                 prompt="Ravi faces west. He turns 135 degrees clockwise, then 270 degrees anticlockwise. Which direction is he facing now?",
                 options=['North-east', 'South-east', 'North-west', 'South-west'], answer=1,
                 explanation="Measuring clockwise from north, west is 270 degrees. Adding 135 gives 405, which is 45 degrees, north-east. Turning 270 degrees anticlockwise is the same as 90 degrees clockwise, so 45 + 90 = 135 degrees, which is south-east. North-east is where he faces after only the first turn.",
                 hint='A large anticlockwise turn can be rewritten as a smaller clockwise one.'),
        ],
    ),
    dict(
        id='guide-reasoning-syllogisms', kind='guide', track='reasoning', drill='syllogisms',
        title='Syllogisms', order=5,
        summary="Draw the statements as Venn diagrams and accept a conclusion only if it holds in every diagram the statements allow.",
        sections=[
            dict(title='The four statement types', text=(
                "Syllogism questions use four kinds of statement, and each has a simple Venn picture.\n\n"
                "All A are B: the A circle sits entirely inside the B circle. A and B could even be the same circle.\n\n"
                "No A is B: the A and B circles are completely separate, with no overlap.\n\n"
                "Some A are B: the circles overlap, so at least one A is also a B. In logic, some means at least one and possibly all, so it does not rule out that every A is a B.\n\n"
                "Some A are not B: at least one A lies outside B. It says nothing about whether other A are inside B.\n\n"
                "Ignore real-world knowledge completely. If the statements say all fish are birds, accept it for the question, even though it is false in real life. "
                "The test is only whether a conclusion follows from the statements given.\n\n"
                "One rule applies throughout this guide, as in most placement tests: every group named in the statements has at least one member. "
                "No circle is ever empty. This is why All A are B lets you conclude Some B are A: there is at least one A, and it is also a B."
            )),
            dict(title='What definitely follows', text=(
                "A conclusion follows only if it is true in every diagram that fits the statements. Being possible is not enough.\n\n"
                "The practical method has two steps. First draw the simplest diagram that fits and check the conclusion. If it is false there, it does not follow. "
                "If it is true, try to break it: redraw the circles in any other way the statements still allow, such as moving a circle outside or adding a separate region, and check again. "
                "Only a conclusion that survives every legal redraw definitely follows.\n\n"
                "A few conversions always hold. All A are B gives Some A are B, and also Some B are A, because the A members, of which there is at least one, are B members too. "
                "Some A are B gives Some B are A. No A is B gives No B is A.\n\n"
                "One conversion does not hold: Some A are not B does not give Some B are not A. "
                "For example, some fruits are not apples, but it does not follow that some apples are not fruits."
            )),
            dict(title='Either-or pairs', text=(
                "Sometimes neither conclusion follows on its own, yet the two together cover every possibility, so one of them must be true. "
                "This happens when the two conclusions are about the same two groups and contradict each other.\n\n"
                "The usual pairs are Some A are B with No A is B, and All A are B with Some A are not B. "
                "Whatever the diagram looks like, exactly one statement in each pair is true. "
                "If a question offers an option such as Either I or II follows, it is meant for this case.\n\n"
                "Use it only when both checks pass: neither conclusion is definite by itself, and the pair really is complementary. "
                "If one of the conclusions already follows on its own, choose that one instead.\n\n"
                "Do not stretch the idea to pairs that merely sound opposite. Some A are B and Some A are not B can both be true at once, so they are not an either-or pair. "
                "The safest habit is to ask two questions: could the two statements ever both be true, and could they ever both be false? If the answer to either is yes, either-or does not apply."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Statements: All pens are tools. Some tools are red. Conclusions: I. Some pens are red. II. Some tools are pens.\n\n"
                "Step 1: draw pens inside tools, and a red circle overlapping tools. "
                "Step 2: test I. The red circle could overlap the tools circle only in the part outside the pens circle. That diagram fits both statements and has no red pens, so I does not follow. "
                "Step 3: test II. Pens are inside tools and pens exist, so some tools are pens in every diagram. II follows. "
                "Answer: only II follows.\n\n"
                "Example 2. Statements: No cats are birds. All birds are animals. Conclusions: I. Some animals are not cats. II. No animals are cats.\n\n"
                "Step 1: draw birds inside animals, and cats separate from birds. "
                "Step 2: test I. Every bird is an animal and no bird is a cat, so the birds are animals that are not cats. I holds in every diagram, so it follows. "
                "Step 3: test II. The cats circle can sit inside the animals circle, away from the birds, and still fit both statements. Then some animals are cats, so II does not follow. "
                "Answer: only I follows."
            )),
        ],
        keyPoints=[
            'A conclusion follows only if it holds in every diagram the statements allow.',
            'Some means at least one, possibly all.',
            'All A are B gives Some B are A; Some A are B gives Some B are A; No A is B gives No B is A.',
            'Some A are not B cannot be turned round.',
            'Either-or applies only to a complementary pair when neither conclusion follows alone.',
            'Ignore real-world facts; use only the statements given.',
        ],
        challenges=[
            dict(id='challenge-reasoning-syllogisms-q1', kind='prediction', title='A chain of alls',
                 prompt="Statements: All roses are flowers. All flowers are plants. Conclusions: I. All roses are plants. II. Some plants are roses.",
                 options=list(SYLLOGISM_OPTIONS), answer=2,
                 explanation="The roses circle sits inside flowers, which sits inside plants, so every rose is a plant and I follows. Since roses exist and all of them are plants, some plants are roses, so II follows as well. Choosing only I misses the rule that All A are B also gives Some B are A.",
                 hint='Draw the three circles and test each conclusion on its own.'),
            dict(id='challenge-reasoning-syllogisms-q2', kind='prediction', title='Two somes',
                 prompt="Statements: Some books are pens. Some pens are cups. Conclusions: I. Some books are cups. II. Some cups are pens.",
                 options=list(SYLLOGISM_OPTIONS), answer=1,
                 explanation="II is just Some pens are cups turned round, which always holds, so II follows. For I, draw the cups circle overlapping the pens circle only in a part away from the books circle. That fits both statements and has no book that is a cup, so I does not follow. Both follow would need a definite link between books and cups, which two some statements never provide.",
                 hint='One conclusion may just be a statement turned round. For the other, try to draw a diagram that fits both statements but makes it false.'),
            dict(id='challenge-reasoning-syllogisms-q3', kind='prediction', title='No and some',
                 prompt="Statements: No metals are liquids. Some liquids are fuels. Conclusions: I. Some fuels are not metals. II. No fuels are metals.",
                 options=list(SYLLOGISM_OPTIONS), answer=0,
                 explanation="Some liquids are fuels, and no liquid is a metal, so those liquid fuels are fuels that are not metals. I holds in every diagram and follows. For II, draw part of the fuels circle outside liquids and overlapping metals. That fits both statements and has fuels that are metals, so II does not follow.",
                 hint='Start from the fuels that are also liquids and ask what you know about them.'),
            dict(id='challenge-reasoning-syllogisms-q4', kind='prediction', title='Nothing certain',
                 prompt="Statements: Some phones are cameras. No camera is a radio. Conclusions: I. Some phones are radios. II. All cameras are phones.",
                 options=list(SYLLOGISM_OPTIONS), answer=3,
                 explanation="Draw radios separate from both phones and cameras: both statements still hold, and no phone is a radio, so I does not follow. Now let part of the cameras circle stick out beyond the phones circle: the statements still hold, and not all cameras are phones, so II does not follow. A diagram can make both false at once, so this is not an either-or pair either. What does follow is Some phones are not radios, but that is not offered.",
                 hint='For each conclusion, try to draw a diagram that fits both statements but makes the conclusion false.'),
            dict(id='challenge-reasoning-syllogisms-q5', kind='prediction', title='Some then all',
                 prompt="Statements: Some teachers are singers. All singers are dancers. Conclusions: I. Some teachers are dancers. II. Some dancers are teachers.",
                 options=list(SYLLOGISM_OPTIONS), answer=2,
                 explanation="The teachers who are singers sit inside the singers circle, which sits inside the dancers circle, so those teachers are dancers and I follows. II is I turned round, and a some statement can always be turned round, so II follows too. Only I would be the choice if you forgot that conversion.",
                 hint='Follow the teachers who are singers into the next circle.'),
        ],
    ),
]
