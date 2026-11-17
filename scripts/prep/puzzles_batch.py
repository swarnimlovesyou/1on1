"""Classic-style puzzles for the puzzles track (Prep), ordered from easier to harder."""

GUIDES = [
    dict(
        id='guide-puzzles-handshakes', kind='guide', track='puzzles', order=1,
        title='Handshakes at a meetup',
        summary='Count every handshake in a room where everyone greets everyone else exactly once.',
        sections=[], challenges=[],
        keyPoints=[
            'Count from one person\'s point of view, then fix the double counting.',
            'Choosing 2 from n is n(n-1)/2.',
            'Check a tiny case (3 or 4 people) by hand before trusting a formula.',
        ],
        puzzle=dict(
            statement=(
                "Fourteen people arrive at a meetup. Before the talks start, every person shakes hands exactly once "
                "with every other person. Nobody shakes their own hand. How many handshakes take place in total?"
            ),
            hints=[
                "How many hands does one person shake? Now multiply by the number of people. Is anything counted twice?",
                "The handshake between Asha and Ben gets counted once from Asha's side and once from Ben's side.",
            ],
            solution=[
                "Each of the 14 people shakes hands with the other 13.",
                "Adding that up over everyone gives 14 x 13 = 182.",
                "Every handshake involves two people, so each one was counted exactly twice in that total.",
                "Divide by 2: 182 / 2 = 91 handshakes. This is the number of ways to choose 2 people from 14.",
            ],
            answer='91',
        ),
    ),
    dict(
        id='guide-puzzles-clock-angle', kind='guide', track='puzzles', order=2,
        title='The angle between the hands',
        summary='Find the angle between the hour and minute hands of a clock at a given time.',
        sections=[], challenges=[],
        keyPoints=[
            'Convert each hand to degrees measured from 12 before comparing.',
            'The hour hand keeps moving between hours, half a degree per minute.',
            'Take the smaller of the two angles the hands make.',
        ],
        puzzle=dict(
            statement=(
                "An ordinary analog clock shows 4:36. Both hands move smoothly and continuously. "
                "What is the smaller angle, in degrees, between the hour hand and the minute hand?"
            ),
            hints=[
                "Work out how far each hand has turned from the 12 o'clock position, in degrees.",
                "The minute hand moves 6 degrees per minute. The hour hand moves 30 degrees per hour plus 0.5 degrees per minute.",
            ],
            solution=[
                "Minute hand: 36 minutes x 6 degrees = 216 degrees from 12.",
                "Hour hand: 4 hours x 30 degrees = 120 degrees, plus 36 minutes x 0.5 degrees = 18 degrees, so 138 degrees from 12.",
                "The difference is 216 - 138 = 78 degrees.",
                "The other way round the dial is 360 - 78 = 282 degrees, so the smaller angle is 78 degrees.",
            ],
            answer='78',
        ),
    ),
    dict(
        id='guide-puzzles-trains-and-bird', kind='guide', track='puzzles', order=3,
        title='Two trains and a restless bird',
        summary='A bird shuttles between two approaching trains; find how far it flies in total.',
        sections=[], challenges=[],
        keyPoints=[
            'Ask how long something lasts before asking where it goes.',
            'An infinite sequence of small trips can still have a simple total.',
            'Closing speed is the sum of two speeds toward each other.',
        ],
        puzzle=dict(
            statement=(
                "Two trains are 150 km apart on the same straight track, heading toward each other. One travels at 40 km/h "
                "and the other at 35 km/h. At the moment they are 150 km apart, a bird leaves the front of the first train and "
                "flies at a constant 90 km/h toward the second. When it reaches the second train it turns instantly and flies "
                "back to the first, and keeps doing this until the trains meet. Turning takes no time. "
                "How many kilometres does the bird fly in total?"
            ),
            hints=[
                "Adding up each leg of the bird's trip is painful. Is there a quantity that is much easier to find?",
                "The bird flies at a fixed speed for the whole time the trains are approaching. How long is that?",
            ],
            solution=[
                "The trains close the gap at 40 + 35 = 75 km/h.",
                "A 150 km gap therefore disappears in 150 / 75 = 2 hours.",
                "The bird flies non-stop at 90 km/h for exactly those 2 hours.",
                "Total distance = 90 x 2 = 180 km. The back-and-forth legs form an infinite series, but it must sum to the same 180 km.",
            ],
            answer='180',
        ),
    ),
    dict(
        id='guide-puzzles-switches-and-bulb', kind='guide', track='puzzles', order=4,
        title='Three switches, one bulb',
        summary='Match three switches to one hidden bulb when you may look at the bulb only once.',
        sections=[], challenges=[],
        keyPoints=[
            'A single observation can carry more than two outcomes if you use more than one property.',
            'Time is a resource: what you do before looking can leave a trace.',
            'Count outcomes: you need at least as many distinguishable results as possibilities.',
        ],
        puzzle=dict(
            statement=(
                "In a hallway there are three ordinary on/off switches. Exactly one of them controls an incandescent bulb in a "
                "closed storeroom at the end of a long corridor; the other two do nothing. From the hallway you cannot see the bulb. "
                "You may flip the switches as often as you like, but you may walk to the storeroom and open the door only once, "
                "and after that you cannot touch the switches again. How can you be certain which switch controls the bulb?"
            ),
            hints=[
                "Looking at the bulb only tells you on or off, which separates two cases, not three. What else can you learn by being in the room?",
                "An incandescent bulb that has been glowing for a while stays warm for some time after it goes dark.",
            ],
            solution=[
                "Call the switches A, B and C. Turn A on and leave it on for about ten minutes.",
                "Turn A off, then turn B on, and walk straight to the storeroom.",
                "If the bulb is lit, B controls it.",
                "If the bulb is dark but warm to the touch, it was on recently, so A controls it.",
                "If the bulb is dark and cold, it was never on, so C controls it.",
                "The three outcomes (lit, dark and warm, dark and cold) are distinct, so one visit always settles the question.",
            ],
        ),
    ),
    dict(
        id='guide-puzzles-lockers', kind='guide', track='puzzles', order=5,
        title='The 120 lockers',
        summary='A crowd of students toggles a row of lockers in a pattern; count how many end up open.',
        sections=[], challenges=[],
        keyPoints=[
            'Follow one item through the whole process instead of following the whole process.',
            'Toggling an even number of times returns to the start.',
            'Divisors come in pairs, except when a number is a perfect square.',
        ],
        puzzle=dict(
            statement=(
                "A corridor has 120 lockers numbered 1 to 120, all closed. 120 students walk past one after another. "
                "Student 1 toggles every locker (opens it if closed, closes it if open). Student 2 toggles every 2nd locker "
                "(2, 4, 6, ...). Student 3 toggles every 3rd locker, and so on, until student 120 toggles only locker 120. "
                "After all 120 students have passed, how many lockers are open?"
            ),
            hints=[
                "Pick one locker, say number 12, and list exactly which students touch it.",
                "Locker n is touched once for each divisor of n. Which numbers have an odd number of divisors?",
            ],
            solution=[
                "Student k touches locker n exactly when k divides n, so locker n is toggled once per divisor of n.",
                "A locker ends up open only if it is toggled an odd number of times.",
                "Divisors pair up as (d, n/d). The pairs are distinct unless d = n/d, which happens only when n is a perfect square.",
                "So exactly the perfect-square lockers have an odd number of divisors and stay open.",
                "The perfect squares up to 120 are 1, 4, 9, ..., 100 (10 squared); 11 squared is 121, which is too big.",
                "Therefore 10 lockers are open.",
            ],
            answer='10',
        ),
    ),
    dict(
        id='guide-puzzles-nine-coins', kind='guide', track='puzzles', order=6,
        title='Nine coins, one heavy',
        summary='Find the one heavier coin among nine using a balance scale as few times as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'A balance has three outcomes, not two, so split into three groups.',
            'Each weighing can at most divide the possibilities by three.',
            'Prove a lower bound by counting outcomes against cases.',
        ],
        puzzle=dict(
            statement=(
                "You have nine coins that look identical. Eight weigh the same and one is slightly heavier. You have a two-pan "
                "balance scale with no weights; each use tells you only whether the left pan is heavier, the right pan is heavier, "
                "or they balance. What is the smallest number of weighings that is guaranteed to find the heavy coin, whatever happens?"
            ),
            hints=[
                "A weighing has three possible results. Can you make each result point to a different group of coins?",
                "Put three coins on each pan and keep three aside. What does each outcome tell you?",
            ],
            solution=[
                "Weighing 1: put coins 1-3 on the left, 4-6 on the right, and keep 7-9 off the scale.",
                "If one pan is heavier, the heavy coin is among its three. If they balance, it is among the three set aside.",
                "Weighing 2: from the suspect three, put one coin on each pan and keep one aside. The heavier pan holds it; a balance means it is the coin set aside.",
                "So 2 weighings always suffice.",
                "One weighing cannot be enough: it has only 3 possible outcomes, but there are 9 possible heavy coins. Hence the minimum is 2.",
            ],
            answer='2',
        ),
    ),
    dict(
        id='guide-puzzles-ferry', kind='guide', track='puzzles', order=7,
        title='The ferry, the dog and the rabbit',
        summary='Get a dog, a rabbit and a basket of carrots across a river without anything being eaten.',
        sections=[], challenges=[],
        keyPoints=[
            'Model the puzzle as states and moves, then search for the shortest path.',
            'Bringing something back can be a forward step.',
            'Identify the item that conflicts with everything and handle it first.',
        ],
        puzzle=dict(
            statement=(
                "A ferry operator must take a dog, a rabbit and a basket of carrots across a river. The boat holds the operator "
                "plus at most one of the three, and only the operator can row it. If the dog and the rabbit are left together on a bank without the operator, the dog "
                "chases the rabbit. If the rabbit and the carrots are left together without the operator, the rabbit eats the "
                "carrots. The dog ignores the carrots. Counting each trip across the river (in either direction) as one crossing, "
                "what is the fewest crossings needed to get all three safely to the far bank?"
            ),
            hints=[
                "Which item is in conflict with both of the others? It has to go first.",
                "At some point the operator must carry something back to the starting bank.",
            ],
            solution=[
                "Crossing 1: take the rabbit over (the dog and carrots are safe together).",
                "Crossing 2: return alone.",
                "Crossing 3: take the dog over. Crossing 4: bring the rabbit back, so the dog is not left with it.",
                "Crossing 5: take the carrots over and leave them with the dog. Crossing 6: return alone.",
                "Crossing 7: take the rabbit over. Everything is across.",
                "Fewer is impossible. The total is odd, since the operator ends on the far bank. If nothing is ever carried back, 5 crossings would mean three loaded trips over with empty returns: the first load must be the rabbit, and the second load would then be left with the rabbit while the operator returns. So something must be carried back and ferried again, which makes at least 7. A full search of all states agrees.",
            ],
            answer='7',
        ),
    ),
    dict(
        id='guide-puzzles-burning-ropes', kind='guide', track='puzzles', order=8,
        title='Timing with two uneven ropes',
        summary='Measure an awkward time interval using two ropes that burn at an uneven rate.',
        sections=[], challenges=[],
        keyPoints=[
            'Lighting both ends halves the remaining time, however uneven the burn.',
            'Use one event (a rope going out) as the trigger for the next action.',
            'Track how much burn time is left on each rope, not how much length.',
        ],
        puzzle=dict(
            statement=(
                "You have two ropes and a box of matches. Rope A takes exactly 10 minutes to burn from one end to the other, and "
                "rope B takes exactly 6 minutes. Both burn unevenly: some stretches burn fast and others slowly, so half the length "
                "does not mean half the time. You may light either end of either rope at any moment, and you can see when a rope "
                "burns out. Starting from the moment you first light something, how can you mark exactly 6.5 minutes?"
            ),
            hints=[
                "If you light a rope at both ends, it burns out in exactly half its remaining time, even though it burns unevenly.",
                "Start A at one end and B at both ends together. What is left of A when B goes out?",
            ],
            solution=[
                "At time 0, light rope A at one end and rope B at both ends.",
                "Burning from both ends, B goes out after 6 / 2 = 3 minutes.",
                "At that moment A has burned for 3 minutes, so it has exactly 7 minutes of burn time left.",
                "Immediately light the other end of A. Burning from both ends, the remaining 7 minutes takes 7 / 2 = 3.5 minutes.",
                "A goes out at 3 + 3.5 = 6.5 minutes after the start, which is the moment you wanted.",
            ],
        ),
    ),
    dict(
        id='guide-puzzles-water-jugs', kind='guide', track='puzzles', order=9,
        title='Six litres from a 4 and a 9',
        summary='Use two unmarked jugs to measure an exact amount of water in as few steps as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'Every reachable state is a pair of amounts; search them breadth-first.',
            'Pouring big into small repeatedly leaves remainders you can collect.',
            'Try filling each jug first; one direction is often much shorter.',
        ],
        puzzle=dict(
            statement=(
                "You have an unmarked 4-litre jug, an unmarked 9-litre jug, a tap and a drain. Both jugs start empty. "
                "One step is any one of: fill a jug to the brim from the tap; empty a jug completely into the drain; or pour from "
                "one jug into the other until the first is empty or the second is full. What is the fewest steps needed to have "
                "exactly 6 litres in one of the jugs?"
            ),
            hints=[
                "Only the 9-litre jug can hold 6 litres. Try starting by filling the big jug rather than the small one.",
                "Filling the 9 and pouring off 4 twice leaves 1 litre. How can that 1 litre help you reach 6?",
            ],
            solution=[
                "Write states as (4-litre, 9-litre). Fill the 9: (0, 9). Pour into the 4: (4, 5).",
                "Empty the 4: (0, 5). Pour again: (4, 1).",
                "Empty the 4: (0, 1). Pour the 1 litre into the 4: (1, 0).",
                "Fill the 9: (1, 9). Pour into the 4 until it is full, which takes 3 litres: (4, 6).",
                "That is 8 steps. A breadth-first search over every reachable state finds no shorter route (starting by filling the 4-litre jug takes longer), so 8 is the minimum.",
            ],
            answer='8',
        ),
    ),
    dict(
        id='guide-puzzles-counterfeit-bag', kind='guide', track='puzzles', order=10,
        title='The counterfeit bag',
        summary='Identify a bag of fake coins with one reading of a digital scale, using as few coins as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'Give each candidate a unique signature in a single measurement.',
            'The excess weight tells you how many fake coins are on the scale.',
            'Zero is a valid label: one candidate can be left out entirely.',
        ],
        puzzle=dict(
            statement=(
                "There are 8 bags, each holding plenty of coins. Every coin in seven of the bags weighs exactly 10 g. Every coin "
                "in the remaining bag is counterfeit and weighs exactly 11 g. You have an accurate digital scale that shows the "
                "total weight, and you may use it only once. You choose some number of coins from each bag (possibly zero) and "
                "weigh them all together. What is the fewest coins you can put on the scale and still be certain which bag is counterfeit?"
            ),
            hints=[
                "If you take a different number of coins from each bag, how does the scale reading reveal the fake bag?",
                "The counts from the 8 bags must all be different. What is the smallest total of 8 different whole numbers that are zero or more?",
            ],
            solution=[
                "If N coins are on the scale and c of them came from the fake bag, the reading is 10 x N + c grams, so the excess over 10 x N equals c.",
                "To tell the bags apart, each bag must give a different excess, so the 8 counts must all be different.",
                "The smallest 8 different non-negative whole numbers are 0, 1, 2, ..., 7.",
                "Take 0 coins from one bag, 1 from the next, and so on up to 7. That is 0 + 1 + ... + 7 = 28 coins.",
                "The excess over 280 g names the bag directly; an excess of 0 means the bag you left out.",
                "Any other set of 8 different counts has a larger sum, so 28 is the minimum.",
            ],
            answer='28',
        ),
    ),
    dict(
        id='guide-puzzles-trimmed-board', kind='guide', track='puzzles', order=11,
        title='Dominoes on a trimmed board',
        summary='Decide whether dominoes can cover a small chessboard that is missing two corners.',
        sections=[], challenges=[],
        keyPoints=[
            'Look for an invariant: a quantity every move preserves.',
            'Colouring is a powerful way to prove that something is impossible.',
            'Counting squares is necessary but not sufficient.',
        ],
        puzzle=dict(
            statement=(
                "A 6 x 6 board is coloured like a chessboard, in alternating black and white squares. Two diagonally opposite "
                "corner squares are cut away, leaving 34 squares. You have 17 dominoes, and each domino covers exactly two squares "
                "that share an edge. Can the 17 dominoes cover the 34 remaining squares with no overlaps and nothing hanging off "
                "the board? Explain why or why not."
            ),
            hints=[
                "The square count works out, so the answer cannot come from counting alone. Think about the colours.",
                "What colours are the two squares under any single domino? What colours were the two corners you removed?",
            ],
            solution=[
                "Any two squares that share an edge have different colours, so every domino covers one black and one white square.",
                "17 dominoes would therefore cover exactly 17 black and 17 white squares.",
                "The full 6 x 6 board has 18 black and 18 white squares.",
                "Diagonally opposite corners always have the same colour, so removing them leaves 18 of one colour and 16 of the other.",
                "17 and 17 can never match 18 and 16, so the covering is impossible, however the dominoes are arranged.",
            ],
        ),
    ),
    dict(
        id='guide-puzzles-ants-on-a-stick', kind='guide', track='puzzles', order=12,
        title='Ants on a metre stick',
        summary='Ants bounce off each other on a stick; find when the last one falls off.',
        sections=[], challenges=[],
        keyPoints=[
            'Two identical objects bouncing apart look the same as passing through each other.',
            'Ignore labels when only the collective outcome matters.',
            'Replace a messy interaction with an equivalent simple one.',
        ],
        puzzle=dict(
            statement=(
                "Five ants sit on a stick 100 cm long, at 10 cm, 25 cm, 40 cm, 70 cm and 85 cm from the left end. They all start "
                "walking at the same moment at 1 cm per second. The ants at 10 cm and 40 cm walk right; the ants at 25 cm, 70 cm and "
                "85 cm walk left. Whenever two ants meet head-on, both instantly turn around and carry on at the same speed. An ant "
                "falls off as soon as it reaches either end of the stick. After how many seconds does the last ant fall off?"
            ),
            hints=[
                "Tracking every bounce is hard. If two ants meet and turn around, what would an observer who cannot tell ants apart see?",
                "Pretend the ants walk straight through each other. Then each 'walker' just goes to the end it is facing.",
            ],
            solution=[
                "When two ants meet and both reverse, the picture is identical to them passing through each other with labels swapped.",
                "So the moments at which ants fall off are the same as if every ant ignored the others and walked straight on.",
                "Walking straight on, the ant at 10 cm heading right needs 90 s; at 25 cm heading left, 25 s; at 40 cm heading right, 60 s; at 70 cm heading left, 70 s; at 85 cm heading left, 85 s.",
                "Ants fall off at 25, 60, 70, 85 and 90 seconds (a different ant may be the one falling each time).",
                "The last ant falls off after 90 seconds.",
            ],
            answer='90',
        ),
    ),
    dict(
        id='guide-puzzles-bridge-and-torch', kind='guide', track='puzzles', order=13,
        title='Four people, one torch, one bridge',
        summary='Get four walkers of different speeds across a narrow bridge at night in the least time.',
        sections=[], challenges=[],
        keyPoints=[
            'Send the two slowest together so their times overlap.',
            'The fastest walkers should do the return trips.',
            'Compare the two standard strategies; neither always wins.',
        ],
        puzzle=dict(
            statement=(
                "Four people must cross a narrow bridge at night. They have one torch, and nobody may be on the bridge without it. "
                "At most two people can be on the bridge at once, and a pair walks at the pace of the slower person. The torch must "
                "be carried back and forth; it cannot be thrown. Alone, the four take 1, 3, 8 and 12 minutes to cross. "
                "What is the shortest total time, in minutes, to get all four across?"
            ),
            hints=[
                "Having the 1-minute person escort everyone wastes time, because the 8 and 12 each pay full price.",
                "What if the 8 and 12 walk over together, and a fast person who is already on the far side brings the torch back?",
            ],
            solution=[
                "1 and 3 cross (3 min). 1 returns with the torch (1 min). Running total 4.",
                "8 and 12 cross together (12 min). 3 returns with the torch (3 min). Running total 19.",
                "1 and 3 cross again (3 min). Total 22 minutes.",
                "The alternative of 1 escorting each person takes 3 + 1 + 8 + 1 + 12 = 25 minutes, which is worse.",
                "A full search of every possible sequence of crossings confirms 22 minutes is the minimum.",
            ],
            answer='22',
        ),
    ),
    dict(
        id='guide-puzzles-poisoned-wine', kind='guide', track='puzzles', order=14,
        title='The poisoned bottle',
        summary='Find one poisoned bottle among hundreds using as few slow test strips as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'When tests run in parallel, give each item a unique pattern of tests.',
            'k yes/no tests can tell apart at most 2 to the power k cases.',
            'Binary numbering is a ready-made way to assign those patterns.',
        ],
        puzzle=dict(
            statement=(
                "A cellar holds 500 bottles of wine, and exactly one is poisoned. A test strip changes colour if it touches even a "
                "drop of the poisoned wine, but only shows its result 24 hours later. You may put drops from as many bottles as you "
                "like on each strip, and every strip must be prepared at the start because you have only 24 hours. What is the fewest "
                "strips you need to be certain which bottle is poisoned?"
            ),
            hints=[
                "After 24 hours each strip is either changed or not. How many different overall results can k strips give?",
                "Number the bottles and write each number in binary. Let each strip stand for one binary digit.",
            ],
            solution=[
                "Each strip ends in one of two states, so k strips give at most 2 to the power k different overall results.",
                "To single out one of 500 bottles you need 2 to the power k to be at least 500. 2 to the 8 is 256, too few; 2 to the 9 is 512, enough.",
                "Number the bottles 0 to 499 and write each in 9-bit binary. Strip i gets a drop from every bottle whose bit i is 1.",
                "After 24 hours, read the changed strips as 1s and the others as 0s. That 9-bit number is the poisoned bottle.",
                "So 9 strips suffice and 8 cannot, which makes 9 the minimum.",
            ],
            answer='9',
        ),
    ),
    dict(
        id='guide-puzzles-missing-and-repeated', kind='guide', track='puzzles', order=15,
        title='One missing, one repeated',
        summary='Spot the missing number and the repeated number in a long list using only a little memory.',
        sections=[], challenges=[],
        keyPoints=[
            'Compare what you see with what you expected; the difference is information.',
            'Two unknowns need two independent equations.',
            'Running totals use constant memory, however long the list.',
        ],
        puzzle=dict(
            statement=(
                "A list should contain each whole number from 1 to n exactly once, in some order. By mistake, one number was "
                "replaced by a copy of another, so one number is missing and one appears twice. The list is read to you once, "
                "one number at a time. You may keep only a few running totals, not the whole list or a checklist of n entries. "
                "How can you find both the missing number and the repeated number?"
            ),
            hints=[
                "Compare the sum you hear with the sum 1 + 2 + ... + n should have. What does the difference tell you?",
                "One equation gives you missing minus repeated. Find a second equation from another running total, such as the sum of squares.",
            ],
            solution=[
                "While the list is read, keep two running totals: the sum S of the numbers and the sum Q of their squares.",
                "The correct totals are n(n+1)/2 for the sum and n(n+1)(2n+1)/6 for the sum of squares.",
                "Let m be the missing number and r the repeated one. Then n(n+1)/2 - S = m - r. Call this d.",
                "Also n(n+1)(2n+1)/6 - Q = m squared - r squared = (m - r)(m + r), so m + r = (that difference) / d.",
                "Solve the two equations: m = ((m + r) + d) / 2 and r = ((m + r) - d) / 2.",
                "Example with n = 6 and list 3, 1, 4, 4, 6, 2: d = 21 - 20 = 1 and 91 - 82 = 9, so m + r = 9, giving m = 5 and r = 4.",
            ],
        ),
    ),
    dict(
        id='guide-puzzles-shared-birthday', kind='guide', track='puzzles', order=16,
        title='Shared birthdays in a group',
        summary='Find how small a group can be while a shared birthday is still more likely than you might expect.',
        sections=[], challenges=[],
        keyPoints=[
            'For "at least one" questions, compute the chance of "none" and subtract from 1.',
            'The number of pairs grows much faster than the number of people.',
            'Multiply the chances step by step as each new person joins.',
        ],
        puzzle=dict(
            statement=(
                "Assume every year has 365 days, nobody is born on 29 February, and each person's birthday is equally likely to be "
                "any day, independently of everyone else. What is the smallest number of people in a group for which the chance "
                "that at least two share a birthday is 70% or more?"
            ),
            hints=[
                "It is easier to work out the chance that all birthdays are different, then take that away from 1.",
                "Each new person must avoid all earlier birthdays: multiply 365/365 x 364/365 x 363/365 and so on until the product falls to 30% or below.",
            ],
            solution=[
                "With n people, the chance that all birthdays differ is (365/365) x (364/365) x ... x ((365 - n + 1)/365).",
                "The chance of at least one shared birthday is 1 minus that product.",
                "Multiplying the terms in turn, at 29 people the chance of a shared birthday is about 68.1%, still below 70%.",
                "At 30 people it is about 70.6%, the first time it reaches 70%.",
                "So the smallest group is 30 people. It is surprisingly small because 30 people form 435 different pairs.",
            ],
            answer='30',
        ),
    ),
    dict(
        id='guide-puzzles-hats-in-a-line', kind='guide', track='puzzles', order=17,
        title='Hats in a line',
        summary='A line of people must guess their own hat colours; plan a strategy that saves as many as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'One bit of shared information can be worth more than one guess.',
            'Parity (odd or even) summarises a whole group in a single bit.',
            'Agree the encoding in advance; then everyone can decode it.',
        ],
        puzzle=dict(
            statement=(
                "Twelve people stand in a single-file line, all facing forward. Each wears a hat that is either black or white, "
                "chosen in any way at all; there may be any number of each colour. Each person can see every hat in front of them, "
                "but not their own or any behind them. Starting from the back of the line and moving forward, each person says "
                "aloud one word, 'black' or 'white', as a guess at their own hat colour, and everyone hears every guess. Nothing "
                "else may be communicated. The group may agree on a strategy beforehand. With the best strategy, how many people "
                "are guaranteed to guess correctly, however the hats are placed?"
            ),
            hints=[
                "The person at the back sees nothing about their own hat, so they can never be sure. Can they help everyone else instead?",
                "The back person's word can carry one bit of information about the hats in front. Which single bit would let everyone else work out their own hat?",
            ],
            solution=[
                "Agree that the person at the back says 'black' if they see an odd number of black hats ahead, and 'white' if even.",
                "The next person counts the black hats they can see. Comparing with the announced parity tells them their own hat colour.",
                "Everyone further forward keeps track of the announced parity and every correct guess made since, plus the hats in front, and so deduces their own colour the same way.",
                "So all 11 people in front of the back person are always right. The back person is right only by luck.",
                "No strategy can guarantee 12: the back person's guess depends only on hats they can see, so for some placement their own hat is the other colour.",
                "The guaranteed number is therefore 11.",
            ],
            answer='11',
        ),
    ),
    dict(
        id='guide-puzzles-two-eggs', kind='guide', track='puzzles', order=18,
        title='Two eggs, eighty floors',
        summary='Find the highest safe floor with only two eggs and the fewest drops in the worst case.',
        sections=[], challenges=[],
        keyPoints=[
            'Balance the worst case: each early step should cost the same total.',
            'Shrink the jump size by one after each survival.',
            'Turn "how many drops for n floors" into "how many floors for d drops".',
        ],
        puzzle=dict(
            statement=(
                "A building has 80 floors. There is some unknown floor at or below which an egg dropped from a window survives, "
                "and above which it breaks; it is possible that eggs survive from every floor, or break from the 1st floor. You "
                "have exactly two identical eggs. A dropped egg that survives can be reused; a broken egg cannot. What is the fewest "
                "drops that guarantees you find the highest floor from which an egg survives, in the worst case?"
            ),
            hints=[
                "Once the first egg breaks, the second egg must check every floor in the remaining gap one at a time, from the bottom up.",
                "If you allow d drops in total, the first drop can be at floor d, the next d - 1 floors higher, and so on. How many floors can d drops cover?",
            ],
            solution=[
                "With the second egg alone you must test floors one by one, so the first egg's job is to narrow down the range.",
                "Suppose you allow d drops in total. Drop the first egg from floor d. If it breaks, the second egg checks floors 1 to d - 1: at most d drops in all.",
                "If it survives, you have d - 1 drops left, so jump up d - 1 floors next, then d - 2, and so on.",
                "This plan covers d + (d - 1) + ... + 1 = d(d + 1)/2 floors. No plan with d drops can cover more: the first drop can be no higher than floor d (if it breaks, every floor below needs its own drop), and if it survives you face the same problem with d - 1 drops.",
                "With d = 12 that is 78 floors, not enough for 80. With d = 13 it is 91 floors, which is enough.",
                "So the minimum worst-case number of drops is 13 (for example, first drops at floors 13, 25, 36, 46, ...).",
            ],
            answer='13',
        ),
    ),
    dict(
        id='guide-puzzles-pirate-vote', kind='guide', track='puzzles', order=19,
        title='Seven pirates split the gold',
        summary='Ruthless, logical pirates vote on how to split treasure; work out what the leader keeps.',
        sections=[], challenges=[],
        keyPoints=[
            'Work backwards from the simplest end state.',
            'A vote is cheap to buy from someone who would otherwise get nothing.',
            'Pin down tie-break rules before reasoning about choices.',
        ],
        puzzle=dict(
            statement=(
                "Seven pirates, ranked from most senior to most junior, must share 60 gold coins, which cannot be cut. The most "
                "senior pirate still on board proposes how to split the coins, and then every pirate on board, including the proposer, "
                "votes. If at least half the votes are yes, the split happens and the game ends. Otherwise the proposer is thrown "
                "overboard and the next most senior pirate proposes, and so on. Every pirate is perfectly logical and knows the others are. "
                "Each pirate wants, in order: first to stay alive, then to get as many coins as possible, and, if those are equal, to "
                "see someone thrown overboard. No promises or deals outside the vote are possible. How many coins does the most senior pirate keep?"
            ),
            hints=[
                "Start with just two pirates left, then three, and build upwards. What does each pirate get in each smaller game?",
                "A pirate votes yes only for strictly more than they would get in the next smaller game. The cheapest votes come from pirates who would get nothing there.",
            ],
            solution=[
                "Number the pirates 1 (most junior) to 7 (most senior). With only pirate 2 and pirate 1, pirate 2's own vote is half, so pirate 2 takes all 60.",
                "Three pirates: pirate 3 needs one more vote. Pirate 1 gets nothing in the two-pirate game, so 1 coin buys that vote: 3 gets 59, 2 gets 0, 1 gets 1.",
                "Four pirates: pirate 4 needs one more vote; pirate 2 gets 0 in the three-pirate game, so give 2 one coin. Split for (4, 3, 2, 1): 59, 0, 1, 0.",
                "Five pirates need 3 votes: the proposer plus pirates 3 and 1, who get 0 in the four-pirate game, at 1 coin each. Split for (5, 4, 3, 2, 1): 58, 0, 1, 0, 1.",
                "Six pirates need 3 votes: the proposer plus pirates 4 and 2 at 1 coin each. Split for (6, 5, 4, 3, 2, 1): 58, 0, 1, 0, 1, 0.",
                "Seven pirates need 4 votes: the proposer plus pirates 5, 3 and 1, who get 0 in the six-pirate game, at 1 coin each.",
                "So the most senior pirate keeps 60 - 3 = 57 coins. Buying votes any cheaper is impossible, since each bought vote must cost at least 1 coin.",
            ],
            answer='57',
        ),
    ),
    dict(
        id='guide-puzzles-horse-races', kind='guide', track='puzzles', order=20,
        title='Thirty-six horses, six lanes',
        summary='Find the three fastest horses using races with no stopwatch, in as few races as possible.',
        sections=[], challenges=[],
        keyPoints=[
            'After each race, cross off everyone who can no longer make the top three.',
            'A horse beaten by three known-faster horses is out.',
            'Prove the lower bound by tracking which horses are still undefeated.',
        ],
        puzzle=dict(
            statement=(
                "There are 36 horses and a track with 6 lanes, so at most 6 horses can run in one race. There is no stopwatch: a race "
                "only tells you the order in which its horses finished. Each horse always runs at exactly the same speed, and no two "
                "horses have the same speed. What is the fewest races that guarantees you can name the fastest, second fastest and "
                "third fastest horses in order?"
            ),
            hints=[
                "Every horse has to race at least once, and the heat winners then need to be compared with each other.",
                "After the heats and a race of heat winners, list only the horses that could still finish in the top three. How many are left?",
            ],
            solution=[
                "Races 1-6: split the horses into six groups of 6 and race each group. Call the groups A to F.",
                "Race 7: race the six group winners. Say the order is A1, B1, C1, D1, E1, F1. A1 is the fastest of all.",
                "Groups D, E and F are out: their winners already trail A1, B1 and C1. C1 can be at best third, so C2 and below are out; B can supply at most B1 and B2; A at most A2 and A3.",
                "Race 8: race the five remaining candidates A2, A3, B1, B2, C1. The top two finishers are second and third overall. So 8 races suffice.",
                "Seven cannot be enough. Call a horse undefeated if it has never finished behind another horse. Any undefeated horse could still be the fastest, so you must get down to 1 undefeated horse: 35 must lose.",
                "Imagine the results are as unhelpful as possible: whenever a race contains an undefeated horse, one of them wins (this never contradicts earlier results). Then a race with u undefeated horses defeats at most u - 1 of them, which is at most 5. Fewer than 7 races cannot defeat 35, and exactly 7 races only can if every race has 6 runners who are all undefeated.",
                "In that case let W, the winner of race 6, also win race 7 (it is still undefeated, so it runs there). Its runner-up in race 6 and the runner-up in race 7 have each lost only to W, and they have never met: both were undefeated before race 6, and the second did not run in race 6. Either could be second fastest, so 7 races cannot guarantee the answer, and 8 is the minimum.",
            ],
            answer='8',
        ),
    ),
]
