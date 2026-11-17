"""Quantitative aptitude guides for the aptitude track (Prep). Checked by check_prep.py."""

GUIDES = [
    dict(
        id='guide-aptitude-percentages', kind='guide', track='aptitude', drill='percentages',
        title='Percentages', order=1,
        summary="Percentages are fractions out of 100, and most questions come down to picking the right base and handling successive changes correctly.",
        sections=[
            dict(title='What a percentage really is', text=(
                "Per cent means per hundred, so p% is just the fraction p/100. Finding p% of a number N is therefore N × p ÷ 100. "
                "For example, 35% of 260 is 260 × 35 ÷ 100 = 91.\n\n"
                "It pays to know a few fraction equivalents, because they turn long multiplication into quick division: "
                "50% = 1/2, 25% = 1/4, 20% = 1/5, 12.5% = 1/8, 33.33% = 1/3, 16.67% = 1/6, 11.11% = 1/9 and 9.09% = 1/11. "
                "So 12.5% of 64 is simply 64 ÷ 8 = 8.\n\n"
                "Percentage change always compares the change with the original value, not the new one:\n\n"
                "Percentage change = (new − old) ÷ old × 100\n\n"
                "If a bus fare goes from ₹240 to ₹282, the change is ₹42 and the increase is 42 ÷ 240 × 100 = 17.5%. "
                "Dividing by the new value (282) is the most common slip, and it gives a wrong answer of about 14.9%."
            )),
            dict(title='Comparing two quantities', text=(
                "Questions often say 'A is r% more than B' and then ask how much less B is than A. "
                "The two answers are not equal, because each percentage is measured against a different base.\n\n"
                "If A is r% more than B, then B is less than A by r ÷ (100 + r) × 100 percent.\n"
                "If A is r% less than B, then B is more than A by r ÷ (100 − r) × 100 percent.\n\n"
                "Picture it with numbers. If X earns 60% more than Y, let Y earn 100, so X earns 160. "
                "The gap is 60, but measured against X's 160 it is only 37.5%. Y earns 37.5% less than X, not 60% less.\n\n"
                "The same idea answers price and consumption questions. If the price of an item rises by r% and a family wants its total spending to stay the same, "
                "it must cut consumption by r ÷ (100 + r) × 100 percent. "
                "If the price falls by r%, it can raise consumption by r ÷ (100 − r) × 100 percent and still spend the same amount."
            )),
            dict(title='Successive changes and percentage points', text=(
                "When a value changes by a% and then by b%, you cannot just add the two. The second change acts on the already changed value. The net effect is\n\n"
                "Net change = a + b + (a × b) ÷ 100 percent\n\n"
                "Use a negative sign for a decrease. A rise of 12% followed by a rise of 25% is 12 + 25 + 300 ÷ 100 = 40%, not 37%. "
                "A useful special case: a rise of x% followed by a fall of x% (in either order) always leaves a net fall of x² ÷ 100 percent. "
                "The value never returns to where it started.\n\n"
                "Be careful when the quantity being changed is itself a percentage, such as an interest rate or a pass rate. "
                "If a rate moves from 6% to 9%, it has risen by 3 percentage points, but by 3 ÷ 6 × 100 = 50 percent. "
                "Both statements are true; they simply measure different things. "
                "Read the question to see which one it wants, and do not mix them up in the options."
            )),
            dict(title='Worked examples', text=(
                "Example 1. A phone costs ₹18,400. Its price is raised by 15% and later the new price is cut by 15%. Find the final price and the net percentage change.\n\n"
                "Step 1: After the rise, price = 18,400 × 115 ÷ 100 = ₹21,160.\n"
                "Step 2: The cut is 15% of 21,160, which is ₹3,174, so the final price = 21,160 − 3,174 = ₹17,986.\n"
                "Step 3: Net change = (17,986 − 18,400) ÷ 18,400 × 100 = −414 ÷ 18,400 × 100 = −2.25%.\n"
                "Shortcut check: 15 − 15 + (15 × −15) ÷ 100 = −2.25%, so the price does not return to where it started.\n\n"
                "Example 2. The price of rice rises by 28%. By what percentage must a household reduce its consumption to keep its monthly spending on rice unchanged?\n\n"
                "Step 1: Required cut = r ÷ (100 + r) × 100 = 28 ÷ 128 × 100 = 21.875%.\n"
                "Step 2: Check with figures. 40 kg at ₹50 per kg costs ₹2,000. The new price is 50 × 1.28 = ₹64 per kg.\n"
                "Step 3: ₹2,000 now buys 2,000 ÷ 64 = 31.25 kg, a drop of 8.75 kg, and 8.75 ÷ 40 × 100 = 21.875%. Both methods agree."
            )),
        ],
        keyPoints=[
            'p% of N is N × p ÷ 100; learn the common fraction equivalents such as 12.5% = 1/8.',
            'Percentage change is always measured against the original value.',
            'If A is r% more than B, B is r ÷ (100 + r) × 100 percent less than A.',
            'Successive changes combine as a + b + ab ÷ 100, never by simple addition.',
            'A change from 6% to 9% is 3 percentage points but a 50 percent increase.',
        ],
        challenges=[
            dict(id='challenge-aptitude-percentages-q1', kind='prediction', title='Two years of growth',
                 prompt="A town has 48,000 residents. Its population grows by 15% in the first year and by 25% in the second year. What is the population after two years?",
                 options=['67,200', '69,000', '60,000'], answer=1,
                 explanation="48,000 × 1.15 = 55,200, then 55,200 × 1.25 = 69,000. The net change is 15 + 25 + (15 × 25) ÷ 100 = 43.75%. Adding the rates to get 40% gives 67,200, which ignores that the second year's growth acts on the larger population.",
                 hint="The second year's growth is calculated on the population at the end of the first year."),
            dict(id='challenge-aptitude-percentages-q2', kind='prediction', title='Less than by how much',
                 prompt="A delivery van carries 40% more parcels a day than a scooter rider. By what percentage does the scooter rider carry fewer parcels than the van?",
                 options=['40%', '71.43%', '28.57%'], answer=2,
                 explanation="Let the rider carry 100 parcels, so the van carries 140. The gap of 40 is measured against the van's 140: 40 ÷ 140 × 100 ≈ 28.57%. Answering 40% uses the rider's load as the base, but this question compares against the van. 71.43% is the rider's load as a percentage of the van's (100 ÷ 140), not how much smaller it is.",
                 hint="Ask whose load the comparison is measured against."),
            dict(id='challenge-aptitude-percentages-q3', kind='prediction', title='Points versus percent',
                 prompt="A college's placement rate climbs from 55% one year to 66% the next. By what percentage has the placement rate increased?",
                 options=['11%', '16.67%', '20%'], answer=2,
                 explanation="The rate rose by 11 percentage points. As a percentage of the old rate, that is 11 ÷ 55 × 100 = 20%. Answering 11% confuses percentage points with percent, and 16.67% divides by the new rate (11 ÷ 66) instead of the old one.",
                 hint="Percentage change is always measured against the starting value."),
            dict(id='challenge-aptitude-percentages-q4', kind='prediction', title='Down then up',
                 prompt="The price of a jacket is reduced by 30%, and the reduced price is then increased by 40%. What is the net effect on the original price?",
                 options=['2% decrease', '10% increase', 'No change', '2% increase'], answer=0,
                 explanation="Net change = −30 + 40 + (−30 × 40) ÷ 100 = 10 − 12 = −2%. On ₹100: 100 → 70 → 70 × 1.4 = 98, a 2% decrease. Saying 10% increase just adds the two rates and forgets that the 40% acts on the smaller, reduced price.",
                 hint="Try it on a starting price of ₹100."),
            dict(id='challenge-aptitude-percentages-q5', kind='prediction', title='Finding the income',
                 prompt="A person spends 35% of monthly income on rent and 40% of what remains on food. If ₹11,700 is left after both, what is the monthly income?",
                 options=['₹46,800', '₹36,000', '₹32,500', '₹30,000'], answer=3,
                 explanation="After rent, 65% of the income remains. Food takes 40% of that, leaving 60% of 65% = 39% of the income. So income = 11,700 ÷ 0.39 = ₹30,000. Adding 35% and 40% to get 75% spent (25% left) gives ₹46,800, but the 40% is a share of the remainder, not of the full income.",
                 hint="Work out what fraction of the whole income is left, one step at a time."),
        ],
    ),
    dict(
        id='guide-aptitude-profit-loss', kind='guide', track='aptitude', drill='profit-loss',
        title='Profit and loss', order=2,
        summary="Profit and loss questions turn on one rule: gain and loss percentages are measured on the cost price, while discounts are measured on the marked price.",
        sections=[
            dict(title='Cost price, selling price and the base', text=(
                "The cost price (CP) is what the seller paid. The selling price (SP) is what the buyer pays. If SP is higher, the difference is profit; if it is lower, the difference is a loss.\n\n"
                "Profit = SP − CP and Loss = CP − SP\n"
                "Profit% = Profit ÷ CP × 100 and Loss% = Loss ÷ CP × 100\n\n"
                "The base is always the cost price unless a question clearly says otherwise. That single fact settles most traps.\n\n"
                "Rearranged forms save time:\n\n"
                "SP = CP × (100 + p) ÷ 100 for a gain of p%\n"
                "SP = CP × (100 − l) ÷ 100 for a loss of l%\n"
                "CP = SP × 100 ÷ (100 + p) when you know SP and the gain\n\n"
                "For instance, an item bought for ₹1,600 and sold at a 12.5% gain fetches 1,600 × 112.5 ÷ 100 = ₹1,800. "
                "If instead an item sold for ₹1,380 at a 15% gain, its cost was 1,380 × 100 ÷ 115 = ₹1,200. "
                "Taking 15% off ₹1,380 gives ₹1,173, which is wrong because the 15% was calculated on CP, not on SP."
            )),
            dict(title='Marked price and discounts', text=(
                "Shops often print a marked price (MP), also called the list price, and then offer a discount on it. A discount is always a percentage of MP:\n\n"
                "SP = MP × (100 − d) ÷ 100\n\n"
                "Two discounts in a row do not add. After the first discount, the second is taken on a smaller price, so the single equivalent discount is\n\n"
                "Equivalent discount = d1 + d2 − (d1 × d2) ÷ 100\n\n"
                "For example, discounts of 10% and 30% equal 10 + 30 − 3 = 37%, not 40%. The order of the two discounts makes no difference.\n\n"
                "When a trader marks goods m% above cost and then allows a d% discount, the overall profit percentage is\n\n"
                "Profit% = m − d − (m × d) ÷ 100\n\n"
                "This is the successive-percentage rule from the percentages guide with the discount written as a negative change. "
                "Marking up by 50% and then giving 20% off leaves 50 − 20 − 10 = 20% profit. If the result is negative, the trader has made a loss."
            )),
            dict(title='Three classic traps', text=(
                "Same selling price, equal gain and loss. If two articles are each sold for the same price, one at x% profit and the other at x% loss, "
                "the seller always makes an overall loss of x² ÷ 100 percent. "
                "The loss happens because the article sold at a loss had a higher cost price, so its loss in rupees outweighs the other article's profit. "
                "The common selling price does not affect the percentage.\n\n"
                "False weights. A dealer who claims to sell at cost but hands over less than the stated weight gains on every sale:\n\n"
                "Gain% = (true weight − weight given) ÷ weight given × 100\n\n"
                "The denominator is the weight actually given, because that is what the dealer really paid for. "
                "A dealer who gives 950 g for every kilogram gains 50 ÷ 950 × 100 ≈ 5.26%, not 5%.\n\n"
                "Articles for the price of others. If the cost price of a articles equals the selling price of b articles, "
                "the result is (a − b) ÷ b × 100 percent. A positive answer is a gain and a negative one is a loss."
            )),
            dict(title='Worked examples', text=(
                "Example 1. A shopkeeper buys a lamp for ₹1,250, marks it 40% above cost and then offers a 15% discount. Find the selling price and the profit percentage.\n\n"
                "Step 1: Marked price = 1,250 × 140 ÷ 100 = ₹1,750.\n"
                "Step 2: Discount = 15% of 1,750 = ₹262.50, so SP = 1,750 − 262.50 = ₹1,487.50.\n"
                "Step 3: Profit = 1,487.50 − 1,250 = ₹237.50, and profit% = 237.50 ÷ 1,250 × 100 = 19%.\n"
                "Shortcut check: m − d − md ÷ 100 = 40 − 15 − 6 = 19%.\n\n"
                "Example 2. A trader sells two used bicycles for ₹9,240 each. On one he gains 12% and on the other he loses 12%. Find his overall gain or loss.\n\n"
                "Step 1: CP of the first = 9,240 × 100 ÷ 112 = ₹8,250.\n"
                "Step 2: CP of the second = 9,240 × 100 ÷ 88 = ₹10,500.\n"
                "Step 3: Total CP = 8,250 + 10,500 = ₹18,750. Total SP = 2 × 9,240 = ₹18,480.\n"
                "Step 4: Loss = 18,750 − 18,480 = ₹270, and loss% = 270 ÷ 18,750 × 100 = 1.44%.\n"
                "Shortcut check: x² ÷ 100 = 144 ÷ 100 = 1.44% loss. The gain and the loss do not cancel."
            )),
        ],
        keyPoints=[
            'Profit and loss percentages are calculated on the cost price.',
            'Discounts are calculated on the marked price.',
            'Two discounts d1 and d2 equal one discount of d1 + d2 − d1d2 ÷ 100.',
            'Equal gain and loss of x% on the same selling price always means a net loss of x² ÷ 100 percent.',
            'With false weights, divide the shortfall by the weight actually given.',
        ],
        challenges=[
            dict(id='challenge-aptitude-profit-loss-q1', kind='prediction', title='Profit on cost',
                 prompt="A trader buys a chair for ₹840 and sells it for ₹966. What is the profit percentage?",
                 options=['13.04%', '12.6%', '15%', '14%'], answer=2,
                 explanation="Profit = 966 − 840 = ₹126. Profit% = 126 ÷ 840 × 100 = 15%. The option 13.04% divides by the selling price (126 ÷ 966), but profit percent is measured on the cost price.",
                 hint="Decide which price is the base for a profit percentage."),
            dict(id='challenge-aptitude-profit-loss-q2', kind='prediction', title='From loss to gain',
                 prompt="Selling a mixer for ₹2,412 causes a 10% loss. At what price should it be sold to make a 15% profit?",
                 options=['₹3,015', '₹2,773.80', '₹3,100', '₹3,082'], answer=3,
                 explanation="First recover the cost: CP = 2,412 × 100 ÷ 90 = ₹2,680. Then SP for a 15% gain = 2,680 × 115 ÷ 100 = ₹3,082. ₹3,015 adds 25% to ₹2,412, and ₹2,773.80 adds 15% to ₹2,412; both treat the old selling price as the base, but both percentages belong to the cost price.",
                 hint="Find the cost price before applying the new percentage."),
            dict(id='challenge-aptitude-profit-loss-q3', kind='prediction', title='Two discounts',
                 prompt="A store offers a 25% discount followed by a further 12% discount on the reduced price. What single discount is equivalent?",
                 options=['37%', '36%', '34%'], answer=2,
                 explanation="Equivalent discount = 25 + 12 − (25 × 12) ÷ 100 = 37 − 3 = 34%. Check on ₹100: 100 → 75 → 75 × 0.88 = 66, which is 34% off. Answering 37% adds the discounts, but the 12% is taken on ₹75, not on ₹100.",
                 hint="Apply both discounts, one after the other, to a ₹100 item."),
            dict(id='challenge-aptitude-profit-loss-q4', kind='prediction', title='Light weights',
                 prompt="A dealer claims to sell rice at cost price but gives only 920 g when a customer pays for 1 kg. What is his gain percentage?",
                 options=['8.70%', '8%', '9.2%'], answer=0,
                 explanation="He pays for 920 g and charges for 1,000 g. Gain% = (1,000 − 920) ÷ 920 × 100 = 80 ÷ 920 × 100 ≈ 8.70%. The option 8% divides by 1,000, but the gain must be compared with what the dealer actually spent, which is the cost of 920 g.",
                 hint="The base is the quantity the dealer actually hands over."),
            dict(id='challenge-aptitude-profit-loss-q5', kind='prediction', title='Same price, equal rates',
                 prompt="Two lamps are sold for ₹7,820 each. One is sold at a 15% profit and the other at a 15% loss. What is the overall result?",
                 options=['No profit, no loss', '2.25% loss', '2.25% gain', '1.5% loss'], answer=1,
                 explanation="CP of the first = 7,820 × 100 ÷ 115 = ₹6,800 and CP of the second = 7,820 × 100 ÷ 85 = ₹9,200. Total CP = ₹16,000 and total SP = ₹15,640, a loss of ₹360, which is 360 ÷ 16,000 × 100 = 2.25%. Shortcut: 15² ÷ 100 = 2.25% loss. Assuming no profit, no loss ignores that the lamp sold at a loss cost more to begin with.",
                 hint="Find each lamp's cost price separately before comparing totals."),
        ],
    ),
    dict(
        id='guide-aptitude-ratio-proportion', kind='guide', track='aptitude', drill='ratio-proportion',
        title='Ratio and proportion', order=3,
        summary="A ratio compares quantities by division, and most questions reduce to finding the value of one part and scaling it.",
        sections=[
            dict(title='Ratios as parts', text=(
                "A ratio a : b says that for every a units of the first quantity there are b units of the second. "
                "It is a comparison, not an amount, so 6 : 9, 2 : 3 and 20 : 30 are the same ratio. "
                "Simplify by dividing both terms by their HCF, after putting both quantities in the same unit: "
                "40 minutes to 2 hours is 40 : 120, which is 1 : 3, not 40 : 2.\n\n"
                "Think of a ratio in parts. If ₹4,500 is split in the ratio 4 : 5, there are 9 parts in all. "
                "One part is 4,500 ÷ 9 = ₹500, so the shares are ₹2,000 and ₹2,500.\n\n"
                "To combine two ratios that share a term, make the shared term equal. Given A : B = 2 : 3 and B : C = 4 : 5, B is 3 in one and 4 in the other. "
                "Scale both to 12: A : B = 8 : 12 and B : C = 12 : 15, so A : B : C = 8 : 12 : 15. "
                "A quick route is A : B : C = (2 × 4) : (3 × 4) : (3 × 5)."
            )),
            dict(title='Proportion and its special terms', text=(
                "Four numbers a, b, c and d are in proportion when a : b = c : d, written a : b :: c : d. "
                "The key property is that the product of the outer terms equals the product of the inner terms:\n\n"
                "a × d = b × c\n\n"
                "Cross-multiplying in this way gives three named terms that come up often.\n\n"
                "Fourth proportional to a, b and c: the d with a : b = c : d, so d = (b × c) ÷ a.\n"
                "Third proportional to a and b: the c with a : b = b : c, so c = b² ÷ a.\n"
                "Mean proportional between a and b: the x with a : x = x : b, so x = √(a × b).\n\n"
                "For example, the third proportional to 4 and 10 is 100 ÷ 4 = 25, because 4 : 10 = 10 : 25. "
                "The mean proportional between 8 and 18 is √144 = 12, because 8 : 12 = 12 : 18. "
                "Note that the mean proportional is a geometric mean, not the ordinary average. "
                "For 8 and 18 the ordinary average would be 13, and 8 : 13 is not equal to 13 : 18."
            )),
            dict(title='Partnership and changing ratios', text=(
                "In a business partnership, profit is shared in proportion to each partner's capital multiplied by the time it was invested:\n\n"
                "Share ratio = (capital of A × months of A) : (capital of B × months of B)\n\n"
                "If one partner puts in ₹20,000 for a full year and another puts in ₹30,000 but joins after four months, "
                "the ratio (working in thousands) is 20 × 12 : 30 × 8 = 240 : 240, or 1 : 1. "
                "Using the capital alone, 2 : 3, is a common mistake.\n\n"
                "Another frequent pattern adds or subtracts the same number from both terms of a ratio. "
                "Write the original quantities as ax and bx, apply the change, set the result equal to the new ratio and cross-multiply to find x.\n\n"
                "There is a built-in sanity check. Adding the same positive number to both terms always moves a ratio towards 1 : 1. "
                "So a ratio below 1 should rise and a ratio above 1 should fall. If your answer moves the other way, recheck the algebra."
            )),
            dict(title='Worked examples', text=(
                "Example 1. A : B = 3 : 5 and B : C = 4 : 7. Divide ₹6,030 among A, B and C in this combined ratio.\n\n"
                "Step 1: Make B equal to 20 in both: A : B = 12 : 20 and B : C = 20 : 35, so A : B : C = 12 : 20 : 35.\n"
                "Step 2: That is 12 + 20 + 35 = 67 parts, and one part = 6,030 ÷ 67 = ₹90.\n"
                "Step 3: A = 12 × 90 = ₹1,080, B = 20 × 90 = ₹1,800 and C = 35 × 90 = ₹3,150, which total ₹6,030.\n\n"
                "Example 2. Two numbers are in the ratio 5 : 8. If 9 is added to each, the ratio becomes 2 : 3. Find the numbers.\n\n"
                "Step 1: Let the numbers be 5x and 8x, so (5x + 9) ÷ (8x + 9) = 2 ÷ 3.\n"
                "Step 2: Cross-multiply: 3(5x + 9) = 2(8x + 9), so 15x + 27 = 16x + 18.\n"
                "Step 3: x = 27 − 18 = 9, so the numbers are 45 and 72.\n"
                "Check: 54 : 81 = 2 : 3, and the ratio rose towards 1, as expected."
            )),
        ],
        keyPoints=[
            'Think of a ratio as parts: find the value of one part, then scale.',
            'Combine A : B and B : C by making the shared term B equal in both.',
            'In a proportion a : b = c : d, the outer product equals the inner product.',
            'The mean proportional of a and b is √(ab), not their average.',
            'Partnership profit is shared in the ratio of capital × time.',
        ],
        challenges=[
            dict(id='challenge-aptitude-ratio-proportion-q1', kind='prediction', title='Fourth proportional',
                 prompt="What is the fourth proportional to 6, 15 and 14?",
                 options=['23', '35', '30', '42'], answer=1,
                 explanation="We need d with 6 : 15 = 14 : d. Cross-multiplying, 6d = 15 × 14 = 210, so d = 35. The option 23 treats the ratio as a difference (15 − 6 = 9, then 14 + 9), but proportion is about multiplying, not adding.",
                 hint="Write the proportion out and cross-multiply."),
            dict(id='challenge-aptitude-ratio-proportion-q2', kind='prediction', title='Mean proportional',
                 prompt="What is the mean proportional between 12 and 75?",
                 options=['43.5', '36', '30', '25'], answer=2,
                 explanation="The mean proportional x satisfies 12 : x = x : 75, so x² = 12 × 75 = 900 and x = 30. Check: 12 : 30 = 2 : 5 and 30 : 75 = 2 : 5. The option 43.5 is the ordinary average of 12 and 75, which does not keep the two ratios equal.",
                 hint="The middle term multiplied by itself equals the product of the outer two."),
            dict(id='challenge-aptitude-ratio-proportion-q3', kind='prediction', title='Capital and time',
                 prompt="P invests ₹40,000 for 12 months and Q invests ₹60,000 for 7 months. Out of a total profit of ₹27,000, what is Q's share?",
                 options=['₹16,200', '₹14,400', '₹13,500', '₹12,600'], answer=3,
                 explanation="Weight each investment by time (in thousands): P = 40 × 12 = 480 and Q = 60 × 7 = 420, so the ratio is 8 : 7. Q's share = 27,000 × 7 ÷ 15 = ₹12,600. ₹16,200 uses capital alone (2 : 3) and forgets that Q's money was in the business for only 7 months; ₹14,400 swaps the two shares.",
                 hint="Profit shares depend on how much was invested and for how long."),
            dict(id='challenge-aptitude-ratio-proportion-q4', kind='prediction', title='Chain of ratios',
                 prompt="If A : B = 2 : 3, B : C = 5 : 4 and C : D = 6 : 7, what is A : D?",
                 options=['5 : 7', '2 : 7', '10 : 21', '4 : 7'], answer=0,
                 explanation="A : D = (A/B) × (B/C) × (C/D) = (2 × 5 × 6) : (3 × 4 × 7) = 60 : 84 = 5 : 7. The option 2 : 7 joins the first term of the first ratio to the last term of the last ratio, ignoring the links in between.",
                 hint="Multiply the ratios together so that B and C cancel out."),
            dict(id='challenge-aptitude-ratio-proportion-q5', kind='prediction', title='After a raise',
                 prompt="The monthly salaries of Asha and Bina are in the ratio 4 : 7. If each gets a raise of ₹3,000, the ratio becomes 7 : 11. What was Asha's salary before the raise?",
                 options=['₹16,800', '₹12,000', '₹9,600', '₹8,400'], answer=2,
                 explanation="Let the salaries be 4x and 7x. Then (4x + 3,000) ÷ (7x + 3,000) = 7 ÷ 11, so 44x + 33,000 = 49x + 21,000, giving 5x = 12,000 and x = 2,400. Asha earned 4 × 2,400 = ₹9,600. Check: 12,600 : 19,800 = 7 : 11. ₹16,800 is Bina's salary, and ₹12,000 is 5x, one step short of the answer.",
                 hint="Write both salaries in terms of one unknown and cross-multiply."),
        ],
    ),
    dict(
        id='guide-aptitude-averages', kind='guide', track='aptitude', drill='averages',
        title='Averages', order=4,
        summary="An average is the total shared out equally, so almost every question is solved by working with totals rather than with the averages directly.",
        sections=[
            dict(title='Average means total divided by count', text=(
                "The average (arithmetic mean) of a set of values is their sum divided by how many there are:\n\n"
                "Average = Sum of values ÷ Number of values, so Sum = Average × Number\n\n"
                "The second form is the one that solves problems. Whenever an average changes, convert both the old and the new averages into totals and look at the difference.\n\n"
                "A handy shortcut when the numbers are close together is the assumed-mean method. "
                "Pick a convenient value near the middle, find how far each value is above or below it, average those deviations and add the result back. "
                "For 47, 52, 49, 55 and 51, assume 50. The deviations are −3, +2, −1, +5 and +1, which sum to 4. "
                "Their average is 4 ÷ 5 = 0.8, so the average is 50.8.\n\n"
                "An average always lies between the smallest and the largest value. If your answer falls outside that range, something has gone wrong."
            )),
            dict(title='Adding, removing and replacing', text=(
                "When one value joins a group of n and the average changes by c, the newcomer differs from the old average by (n + 1) × c:\n\n"
                "New value = old average + (n + 1) × change in average\n\n"
                "The logic: the newcomer must bring the old average for itself, plus enough extra to lift each of the n + 1 members by c. If the average falls, c is negative.\n\n"
                "When one member leaves a group of n and the average of the rest changes by c, the person who left equals old average − (n − 1) × c.\n\n"
                "Replacement is different because the group size stays at n. If one member is swapped for another and the average rises by c, the total rose by n × c, so\n\n"
                "New member = member replaced + n × change in average\n\n"
                "For example, if replacing a 40 kg child in a group of 6 raises the average by 0.5 kg, the newcomer weighs 40 + 6 × 0.5 = 43 kg. "
                "Using n + 1 instead of n here is a frequent slip."
            )),
            dict(title='Weighted averages and evenly spaced numbers', text=(
                "When groups of different sizes are combined, you cannot simply average their averages. Each group's average must be weighted by its size:\n\n"
                "Combined average = (n1 × a1 + n2 × a2) ÷ (n1 + n2)\n\n"
                "The combined average always lies between a1 and a2, and closer to the average of the larger group.\n\n"
                "For numbers in an arithmetic progression, where each term differs from the previous one by the same amount, the average is simply\n\n"
                "Average = (first term + last term) ÷ 2\n\n"
                "So the average of all multiples of 4 from 12 to 60 is (12 + 60) ÷ 2 = 36. "
                "With an odd count the average is the middle term; with an even count it is the mean of the two middle terms.\n\n"
                "Two useful consequences: the average of the first n natural numbers is (n + 1) ÷ 2, and the average of the first n odd numbers is n."
            )),
            dict(title='Worked examples', text=(
                "Example 1. The average weight of 14 students is 52 kg. When their teacher's weight is included, the average rises by 1.5 kg. Find the teacher's weight.\n\n"
                "Step 1: Total for the students = 14 × 52 = 728 kg.\n"
                "Step 2: The new average is 52 + 1.5 = 53.5 kg across 15 people, so the new total = 15 × 53.5 = 802.5 kg.\n"
                "Step 3: Teacher's weight = 802.5 − 728 = 74.5 kg.\n"
                "Shortcut check: old average + (n + 1) × change = 52 + 15 × 1.5 = 74.5 kg.\n\n"
                "Example 2. Section A has 32 students with an average score of 68, and Section B has 48 students with an average score of 73. Find the average of all 80 students.\n\n"
                "Step 1: Total for A = 32 × 68 = 2,176.\n"
                "Step 2: Total for B = 48 × 73 = 3,504.\n"
                "Step 3: Combined average = (2,176 + 3,504) ÷ 80 = 5,680 ÷ 80 = 71.\n"
                "Check: the simple mean of 68 and 73 is 70.5, but the true answer is pulled towards 73 because Section B is the larger group."
            )),
        ],
        keyPoints=[
            'Turn averages into totals: Sum = Average × Number.',
            'A newcomer who shifts the average by c differs from the old average by (n + 1) × c.',
            'In a replacement the group size stays n, so the total changes by n × c.',
            'Combine groups with a weighted average, never by averaging the averages.',
            'For evenly spaced numbers, average = (first + last) ÷ 2.',
        ],
        challenges=[
            dict(id='challenge-aptitude-averages-q1', kind='prediction', title='Evenly spaced',
                 prompt="What is the average of all multiples of 7 from 21 to 98, inclusive?",
                 options=['56', '63', '59', '59.5'], answer=3,
                 explanation="The multiples of 7 form an arithmetic progression, so the average is (21 + 98) ÷ 2 = 119 ÷ 2 = 59.5. Check: there are 12 terms (7 × 3 up to 7 × 14) with a total of 714, and 714 ÷ 12 = 59.5. The option 59 drops the half; the average of evenly spaced whole numbers need not be a whole number.",
                 hint="For evenly spaced numbers, only the first and last terms matter."),
            dict(id='challenge-aptitude-averages-q2', kind='prediction', title='One value swapped',
                 prompt="The average of 9 numbers is 46. If one of them, 58, is replaced by 31, what is the new average?",
                 options=['43', '43.3', '46'], answer=0,
                 explanation="The total drops by 58 − 31 = 27. Spread over 9 numbers, the average drops by 27 ÷ 9 = 3, giving 46 − 3 = 43. Check: 9 × 46 = 414 and 414 − 27 = 387 = 9 × 43. The option 43.3 divides the drop by 10, but a swap leaves the group at 9 numbers.",
                 hint="Find how much the total changes, then share that change among the numbers."),
            dict(id='challenge-aptitude-averages-q3', kind='prediction', title='A big innings',
                 prompt="Scoring 126 runs in her 21st match lifts a batter's average by 3 runs. What is her average after the 21st match?",
                 options=['63', '69', '66', '60'], answer=2,
                 explanation="Let the average after 20 matches be a. Then 20a + 126 = 21(a + 3), so 20a + 126 = 21a + 63 and a = 63. The new average is 63 + 3 = 66. Check: 20 × 63 = 1,260 and (1,260 + 126) ÷ 21 = 1,386 ÷ 21 = 66. The option 63 is the average before the 21st match, not after it.",
                 hint="Write the total runs before and after the 21st match using one unknown."),
            dict(id='challenge-aptitude-averages-q4', kind='prediction', title='Replacement',
                 prompt="In a group of 8 workers, one worker weighing 61 kg is replaced by a new worker, and the group's average weight goes up by 2.5 kg. What does the new worker weigh?",
                 options=['63.5 kg', '81 kg', '83.5 kg', '41 kg'], answer=1,
                 explanation="The group still has 8 people, so the total went up by 8 × 2.5 = 20 kg, and the new worker weighs 61 + 20 = 81 kg. The option 83.5 kg uses 9 × 2.5 = 22.5, which applies only when someone joins without anyone leaving; 63.5 kg adds the change in average just once.",
                 hint="The number of people stays the same, but the total does not."),
            dict(id='challenge-aptitude-averages-q5', kind='prediction', title='The middle number',
                 prompt="The average of 21 numbers is 32. The average of the first 11 is 30 and the average of the last 11 is 36. What is the 11th number?",
                 options=['33', '42', '54', '66'], answer=2,
                 explanation="The first 11 total 11 × 30 = 330 and the last 11 total 11 × 36 = 396. Together that is 726, but the 11th number is counted in both groups. All 21 numbers total 21 × 32 = 672, so the 11th number = 726 − 672 = 54. The option 33 is just the mean of 30 and 36, which ignores the totals.",
                 hint="Add the two partial totals and compare them with the overall total."),
        ],
    ),
    dict(
        id='guide-aptitude-interest', kind='guide', track='aptitude', drill='interest',
        title='Simple and compound interest', order=5,
        summary="Simple interest adds the same amount every year, while compound interest earns interest on interest, and the gap between them follows neat formulas.",
        sections=[
            dict(title='Simple interest', text=(
                "Under simple interest (SI), interest is calculated only on the original principal, so the same amount is added every year.\n\n"
                "SI = P × R × T ÷ 100 and Amount A = P + SI\n\n"
                "Here P is the principal in rupees, R is the rate per cent per annum and T is the time in years. "
                "If time is given in months, divide by 12: 9 months is 0.75 years.\n\n"
                "Rearranging gives the other unknowns: P = SI × 100 ÷ (R × T), R = SI × 100 ÷ (P × T) and T = SI × 100 ÷ (P × R).\n\n"
                "Because SI grows by a fixed amount each year, two amounts at different times reveal it directly. "
                "If a sum grows to ₹5,600 in 2 years and to ₹6,200 in 4 years, the yearly interest is (6,200 − 5,600) ÷ 2 = ₹300. "
                "Working backwards, P = 5,600 − 2 × 300 = ₹5,000, and the rate is 300 ÷ 5,000 × 100 = 6%.\n\n"
                "A sum doubles under SI when the total interest equals P, that is, when R × T = 100."
            )),
            dict(title='Compound interest', text=(
                "Under compound interest (CI), each year's interest is added to the principal and itself earns interest in later years.\n\n"
                "A = P × (1 + R ÷ 100)^T and CI = A − P\n\n"
                "The growth factor (1 + R ÷ 100) is the same multiplier used for successive percentage increases. "
                "Over two years the effective rate is 2R + R² ÷ 100 percent, which is exactly the a + b + ab ÷ 100 rule with a = b = R. "
                "At 10% per annum, two years of compounding give 21%, not 20%.\n\n"
                "When interest is compounded more often than once a year, divide the rate and multiply the number of periods:\n\n"
                "Half-yearly: rate R ÷ 2 per half-year, for 2T periods.\n"
                "Quarterly: rate R ÷ 4 per quarter, for 4T periods.\n\n"
                "So 12% per annum compounded quarterly for one year means 3% per quarter for 4 quarters, a factor of 1.03⁴ ≈ 1.1255, slightly better than 12%.\n\n"
                "If the rate differs from year to year, multiply the separate factors: 5% and then 8% gives 1.05 × 1.08 = 1.134."
            )),
            dict(title='CI minus SI, and growth patterns', text=(
                "For the same principal, rate and whole number of years, compound interest is never less than simple interest. "
                "With yearly compounding the two are equal for the first year, and after that the gap has closed forms:\n\n"
                "For 2 years: CI − SI = P × (R ÷ 100)²\n"
                "For 3 years: CI − SI = P × (R ÷ 100)² × (3 + R ÷ 100)\n\n"
                "The 2-year gap is simply the interest earned in year two on year one's interest.\n\n"
                "Compound growth also follows a multiplying pattern. If a sum doubles in n years at a fixed compound rate, "
                "it becomes 4 times in 2n years and 8 times in 3n years, because each block of n years multiplies the money by 2 again. "
                "Simple interest behaves differently: if a sum doubles in n years under SI, it becomes 3 times in 2n years and 4 times in 3n years, since only the original principal earns interest.\n\n"
                "Finally, when compound amounts are given for two consecutive years, the rate comes from their ratio: A2 ÷ A1 = 1 + R ÷ 100."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Find the simple interest and the amount on ₹18,500 at 7.5% per annum for 4 years.\n\n"
                "Step 1: SI = P × R × T ÷ 100 = 18,500 × 7.5 × 4 ÷ 100.\n"
                "Step 2: R × T = 7.5 × 4 = 30, so SI = 18,500 × 30 ÷ 100 = ₹5,550.\n"
                "Step 3: Amount = 18,500 + 5,550 = ₹24,050.\n\n"
                "Example 2. Find the compound interest on ₹25,000 at 8% per annum, compounded annually, for 3 years, and compare it with the simple interest.\n\n"
                "Step 1: The growth factor is 1.08, so A = 25,000 × 1.08³.\n"
                "Step 2: Year by year: 25,000 × 1.08 = 27,000; 27,000 × 1.08 = 29,160; 29,160 × 1.08 = 31,492.80.\n"
                "Step 3: CI = 31,492.80 − 25,000 = ₹6,492.80.\n"
                "Step 4: SI on the same terms = 25,000 × 8 × 3 ÷ 100 = ₹6,000, so CI − SI = ₹492.80.\n"
                "Shortcut check: P × (R ÷ 100)² × (3 + R ÷ 100) = 25,000 × 0.0064 × 3.08 = 492.80."
            )),
        ],
        keyPoints=[
            'SI = P × R × T ÷ 100, and it adds the same amount every year.',
            'Compound amount A = P × (1 + R ÷ 100)^T.',
            'For half-yearly compounding, halve the rate and double the number of periods.',
            'For 2 years, CI − SI = P × (R ÷ 100)².',
            'Under CI, if money doubles in n years it becomes 8 times in 3n years.',
        ],
        challenges=[
            dict(id='challenge-aptitude-interest-q1', kind='prediction', title='Two amounts at simple interest',
                 prompt="At simple interest, a sum grows to ₹15,200 in 3 years and to ₹16,800 in 5 years. What is the principal?",
                 options=['₹12,800', '₹11,200', '₹13,600', '₹12,000'], answer=0,
                 explanation="The extra 2 years add 16,800 − 15,200 = ₹1,600, so SI is ₹800 a year. Three years of interest is ₹2,400, so P = 15,200 − 2,400 = ₹12,800 (and the rate is 800 ÷ 12,800 × 100 = 6.25%). ₹11,200 subtracts 5 years of interest from the 3-year amount.",
                 hint="Use the difference between the two amounts to find one year's interest."),
            dict(id='challenge-aptitude-interest-q2', kind='prediction', title='The two-year gap',
                 prompt="What is the difference between compound interest and simple interest on ₹15,000 at 12% per annum for 2 years, compounded annually?",
                 options=['₹180', '₹3,600', '₹432', '₹216'], answer=3,
                 explanation="CI − SI for 2 years = P × (R ÷ 100)² = 15,000 × 0.12 × 0.12 = ₹216. Directly: A = 15,000 × 1.12² = 18,816, so CI = 3,816, while SI = 15,000 × 12 × 2 ÷ 100 = 3,600, and 3,816 − 3,600 = 216. ₹3,600 is the simple interest itself, not the difference.",
                 hint="The gap comes only from interest earned on the first year's interest."),
            dict(id='challenge-aptitude-interest-q3', kind='prediction', title='Half-yearly compounding',
                 prompt="What is the compound interest on ₹20,000 at 10% per annum for 1 year, compounded half-yearly?",
                 options=['₹2,000', '₹2,050', '₹2,100', '₹2,025'], answer=1,
                 explanation="Half-yearly means 5% per half-year for 2 half-years. A = 20,000 × 1.05² = 20,000 × 1.1025 = ₹22,050, so CI = ₹2,050. ₹2,000 compounds only once in the year, which for a single year is the same as simple interest.",
                 hint="Halve the rate and double the number of periods."),
            dict(id='challenge-aptitude-interest-q4', kind='prediction', title='From double to eight times',
                 prompt="An investment earning a fixed rate of compound interest is worth 3 times its starting value after 4 years. After how many years will it be worth 81 times its starting value?",
                 options=['108', '160', '16', '12'], answer=2,
                 explanation="Each 4-year block multiplies the money by 3. Eighty-one times is 3 × 3 × 3 × 3, so it takes four blocks: 4 × 4 = 16 years. 108 years scales the time in proportion to the multiple (81 ÷ 3 × 4), and 160 years is the simple-interest answer (80 lots of P at 2P per 4 years); 12 years reaches only 27 times.",
                 hint="Ask what each 4-year block does to the money."),
            dict(id='challenge-aptitude-interest-q5', kind='prediction', title='Finding the rate',
                 prompt="₹6,250 grows to ₹7,290 in 2 years at compound interest, compounded annually. What is the rate per annum?",
                 options=['8.32%', '8%', '9%', '16.64%'], answer=1,
                 explanation="7,290 ÷ 6,250 = 1.1664 = 1.08², so 1 + R ÷ 100 = 1.08 and R = 8%. Check: 6,250 × 1.08 = 6,750 and 6,750 × 1.08 = 7,290. The option 8.32% treats the gain as simple interest (1,040 ÷ 6,250 ÷ 2 × 100), which overstates the rate because it ignores interest on interest.",
                 hint="Divide the amount by the principal and look for a perfect square."),
        ],
    ),
    dict(
        id='guide-aptitude-time-work', kind='guide', track='aptitude', drill='time-work',
        title='Time and work', order=6,
        summary="Time and work problems become simple once you think in terms of work done per day and give the whole job a convenient number of units.",
        sections=[
            dict(title='Work as a rate', text=(
                "If a person can finish a job in n days, they do 1/n of it each day. When people work together their rates add; their times do not:\n\n"
                "If A takes a days and B takes b days, together they do 1/a + 1/b of the job per day, and the time together = (a × b) ÷ (a + b) days.\n\n"
                "Fractions get messy with three or more workers, so a cleaner method is to set the total work equal to the LCM of the individual times. "
                "Suppose P takes 8 days and Q takes 12 days. Call the job 24 units. P does 24 ÷ 8 = 3 units a day and Q does 24 ÷ 12 = 2 units a day. "
                "Together they do 5 units a day and finish in 24 ÷ 5 = 4.8 days.\n\n"
                "Never average the times. Working together must be faster than the faster worker alone, "
                "so 4.8 days, less than P's 8 days, passes the sanity check, while the average of 10 days does not.\n\n"
                "If one worker is k times as efficient as another, they take 1/k of the time."
            )),
            dict(title='Efficiency and the worker-days rule', text=(
                "Efficiency and time are inversely proportional. If the efficiencies of A and B are in the ratio 3 : 2, their times for the same job are in the ratio 2 : 3.\n\n"
                "When many workers of equal ability share a job, the total effort can be measured in worker-days or worker-hours. "
                "More workers, more days or longer hours all produce more work, which gives the rule\n\n"
                "(M1 × D1 × H1) ÷ W1 = (M2 × D2 × H2) ÷ W2\n\n"
                "where M is the number of workers, D the days, H the hours per day and W the amount of work. "
                "Leave out any factor that does not change between the two situations.\n\n"
                "The same idea handles workers joining or leaving midway. Find the total worker-days the job needs, subtract the worker-days already done, "
                "and divide the rest by the new number of workers. For example, if 10 workers would take 9 days (90 worker-days) and 4 more join after 2 days, "
                "then 90 − 20 = 70 worker-days remain, which 14 workers finish in 5 more days, 7 days in all."
            )),
            dict(title='Pipes and cisterns', text=(
                "Pipes and cisterns are time-and-work questions in disguise. A pipe that fills a tank in n hours does 1/n of the job per hour, "
                "and a pipe or leak that empties it in m hours does −1/m of the job per hour. Add the rates of whatever is open:\n\n"
                "Net rate = sum of filling rates − sum of emptying rates\n\n"
                "The LCM method works here too. Say an inlet fills a tank in 6 hours and an outlet empties it in 9 hours. Take the tank as 18 units. "
                "The inlet adds 3 units an hour and the outlet removes 2, so with both open the tank gains 1 unit an hour and fills in 18 hours.\n\n"
                "Watch the sign. Treating the outlet as a helper and adding 3 + 2 would give 18 ÷ 5 = 3.6 hours, "
                "which is faster than the inlet alone and so cannot be right when something is draining the tank.\n\n"
                "If the net rate is negative, a full tank empties instead, and the same arithmetic tells you how quickly."
            )),
            dict(title='Worked examples', text=(
                "Example 1. A can finish a job in 12 days and B in 18 days. They start together, but A leaves after 4 days. How many days does the whole job take?\n\n"
                "Step 1: Take the job as LCM(12, 18) = 36 units, so A does 3 units a day and B does 2.\n"
                "Step 2: In 4 days together they complete 4 × 5 = 20 units.\n"
                "Step 3: B does the remaining 36 − 20 = 16 units alone in 16 ÷ 2 = 8 days, so the job takes 4 + 8 = 12 days.\n\n"
                "Example 2. 18 workers, working 8 hours a day, lay 540 m of pipe in 15 days. How many days will 24 workers, working 6 hours a day, take to lay 720 m?\n\n"
                "Step 1: Use (M1 × D1 × H1) ÷ W1 = (M2 × D2 × H2) ÷ W2.\n"
                "Step 2: Left side = 18 × 15 × 8 ÷ 540 = 2,160 ÷ 540 = 4.\n"
                "Step 3: Right side = 24 × D × 6 ÷ 720 = D ÷ 5, so D ÷ 5 = 4 and D = 20 days.\n"
                "Sense check: more pipe and shorter hours push the time up, more workers push it down."
            )),
        ],
        keyPoints=[
            'Rates add, times do not: together, A and B take ab ÷ (a + b) days.',
            'Set the total work to the LCM of the individual times to avoid fractions.',
            'Efficiency is inversely proportional to time.',
            'Use (M1 × D1 × H1) ÷ W1 = (M2 × D2 × H2) ÷ W2 for groups of equal workers.',
            'In pipes and cisterns, emptying rates are subtracted.',
        ],
        challenges=[
            dict(id='challenge-aptitude-time-work-q1', kind='prediction', title='Working together',
                 prompt="X can finish a task in 20 days and Y in 30 days. How long will they take working together?",
                 options=['25 days', '12 days', '10 days', '50 days'], answer=1,
                 explanation="Take the task as 60 units. X does 3 units a day and Y does 2, so together they do 5 units a day and finish in 60 ÷ 5 = 12 days. Equivalently, 20 × 30 ÷ (20 + 30) = 600 ÷ 50 = 12. The option 25 days averages the times, but two people working together must finish faster than either alone.",
                 hint="Add the daily rates, not the numbers of days."),
            dict(id='challenge-aptitude-time-work-q2', kind='prediction', title='Twice as efficient',
                 prompt="A is twice as efficient as B. Working together, they finish a job in 14 days. How long would A take alone?",
                 options=['28 days', '42 days', '21 days', '7 days'], answer=2,
                 explanation="Give A 2 units a day and B 1 unit a day. Together they do 3 units a day for 14 days, so the job is 42 units. A alone takes 42 ÷ 2 = 21 days. 42 days is B's time alone, and 28 days simply doubles the joint time.",
                 hint="Assign daily units in the ratio of efficiency, then find the size of the job."),
            dict(id='challenge-aptitude-time-work-q3', kind='prediction', title='A leaking tank',
                 prompt="A pipe fills a tank in 12 hours. A leak at the bottom could empty the full tank in 30 hours. With the leak open, how long does the pipe take to fill the empty tank?",
                 options=['20 hours', '8 4/7 hours', '18 hours', '42 hours'], answer=0,
                 explanation="Take the tank as 60 units. The pipe adds 5 units an hour and the leak removes 2, so the net gain is 3 units an hour and the tank fills in 60 ÷ 3 = 20 hours. The option 8 4/7 hours adds the leak's rate instead of subtracting it, as if the leak were helping to fill the tank.",
                 hint="The leak works against the pipe."),
            dict(id='challenge-aptitude-time-work-q4', kind='prediction', title='Reinforcements',
                 prompt="15 workers can finish a job in 28 days. After 8 days of work, 5 more workers of the same ability join. In how many days in total is the job finished?",
                 options=['15 days', '21 days', '25 days', '23 days'], answer=3,
                 explanation="The job needs 15 × 28 = 420 worker-days. In 8 days, 15 workers do 120, leaving 300. With 20 workers that takes 300 ÷ 20 = 15 more days, so the total is 8 + 15 = 23 days. The option 15 days counts only the time after the new workers join, and 21 days would be right only if all 20 had worked from the start.",
                 hint="Count the total worker-days the job needs, then subtract what is already done."),
            dict(id='challenge-aptitude-time-work-q5', kind='prediction', title='Pairs of workers',
                 prompt="Painters P and Q can paint a hall in 18 days, Q and R in 24 days, and P and R in 36 days. If all three work together, how many days will the hall take?",
                 options=['8 days', '16 days', '26 days', '12 days'], answer=1,
                 explanation="Take the job as LCM(18, 24, 36) = 72 units. P + Q = 4, Q + R = 3 and P + R = 2 units a day. Adding gives 2(P + Q + R) = 9, so P + Q + R = 4.5 units a day and the hall takes 72 ÷ 4.5 = 16 days. The option 8 days uses 9 units a day, forgetting that adding the three pairs counts each painter twice; 26 days averages the three times.",
                 hint="Add the three pair-rates and ask how many times each person has been counted."),
        ],
    ),
    dict(
        id='guide-aptitude-speed-distance', kind='guide', track='aptitude', drill='speed-distance',
        title='Speed, distance and time', order=7,
        summary="Distance equals speed times time; the rest is converting units correctly and knowing when to add or subtract speeds.",
        sections=[
            dict(title='The core relation and units', text=(
                "Every question here rests on one relation:\n\n"
                "Distance = Speed × Time, so Speed = Distance ÷ Time and Time = Distance ÷ Speed\n\n"
                "The units must match. To convert km/h to m/s multiply by 5/18, and to go back multiply by 18/5. "
                "This works because 1 km/h = 1,000 m ÷ 3,600 s = 5/18 m/s. So 90 km/h is 25 m/s, and 12 m/s is 43.2 km/h.\n\n"
                "When the distance is fixed, speed and time are inversely proportional. If speeds are in the ratio a : b, the times are in the ratio b : a. "
                "This gives a quick route through 'late' and 'early' problems: travelling at 3/4 of the usual speed takes 4/3 of the usual time, "
                "so the delay equals 1/3 of the usual time.\n\n"
                "Before reaching for a formula, write down what the question holds fixed: the distance, the time or the speed."
            )),
            dict(title='Average speed', text=(
                "Average speed is total distance divided by total time. It is not the average of the speeds unless equal times are spent at each speed.\n\n"
                "Average speed = total distance ÷ total time\n\n"
                "When equal distances are covered at speeds x and y, as on a trip out and back, the average speed is\n\n"
                "Average speed = 2xy ÷ (x + y)\n\n"
                "For 36 km/h one way and 54 km/h back, that gives 2 × 36 × 54 ÷ 90 = 43.2 km/h, not 45. "
                "Confirm it with a convenient distance of 108 km each way: 3 hours out and 2 hours back, so 216 km in 5 hours, which is 43.2 km/h. "
                "The slower leg gets more weight because more time is spent on it.\n\n"
                "For three equal distances at x, y and z, the formula becomes 3xyz ÷ (xy + yz + zx). "
                "If instead equal times are spent at each speed, the simple average (x + y) ÷ 2 is correct."
            )),
            dict(title='Relative speed and trains', text=(
                "When two objects move, what matters for meeting or passing is their relative speed:\n\n"
                "Moving in opposite directions: relative speed = sum of the speeds\n"
                "Moving in the same direction: relative speed = difference of the speeds\n\n"
                "Train problems add one twist: a train has length, so passing something means covering extra distance.\n\n"
                "Passing a pole, a signal post or a person standing still: time = length of train ÷ speed.\n"
                "Passing a platform, bridge or tunnel: time = (length of train + length of platform) ÷ speed.\n"
                "Two trains passing each other: time = (sum of their lengths) ÷ relative speed.\n"
                "Passing a walking person: treat the person as a pole but use the relative speed.\n\n"
                "Convert speeds to m/s when lengths are in metres. A 120 m train at 36 km/h (10 m/s) passes a pole in 12 seconds, "
                "and the same train needs (120 + 180) ÷ 10 = 30 seconds to clear a 180 m bridge."
            )),
            dict(title='Boats and streams', text=(
                "Let a boat's speed in still water be u and the stream's speed be v. Going with the current (downstream) the speeds add, and against it (upstream) they subtract:\n\n"
                "Downstream speed = u + v and Upstream speed = u − v\n\n"
                "Turning these round gives the two values questions usually ask for:\n\n"
                "u = (downstream + upstream) ÷ 2 and v = (downstream − upstream) ÷ 2\n\n"
                "For example, if a boat goes downstream at 15 km/h and upstream at 9 km/h, its still-water speed is 12 km/h and the stream flows at 3 km/h. "
                "Forgetting to halve is the commonest slip here.\n\n"
                "A round trip on a river behaves like the average-speed case: equal distances at two different speeds. "
                "With the numbers above, the average speed for going down and back up the same stretch is 2 × 15 × 9 ÷ 24 = 11.25 km/h, "
                "which is less than the still-water speed of 12 km/h. A current always slows a round trip."
            )),
            dict(title='Worked examples', text=(
                "Example 1. A train 210 m long runs at 54 km/h. How long does it take to cross a platform 330 m long?\n\n"
                "Step 1: Convert the speed: 54 × 5/18 = 15 m/s.\n"
                "Step 2: To clear the platform, the train covers its own length plus the platform's: 210 + 330 = 540 m, taking 540 ÷ 15 = 36 seconds.\n"
                "Using only 330 m gives 22 seconds, which stops the clock when the engine, not the last coach, leaves the platform.\n\n"
                "Example 2. Two trains, 180 m and 150 m long, run on parallel tracks at 64 km/h and 46 km/h. "
                "How long do they take to pass each other completely (a) when moving in the same direction and (b) when moving in opposite directions?\n\n"
                "Step 1: In both cases the distance is 180 + 150 = 330 m.\n"
                "Step 2 (a): Relative speed = 64 − 46 = 18 km/h = 5 m/s. Time = 330 ÷ 5 = 66 seconds.\n"
                "Step 3 (b): Relative speed = 64 + 46 = 110 km/h = 275/9 m/s. Time = 330 × 9 ÷ 275 = 10.8 seconds.\n"
                "Passing head-on is far quicker because the relative speed is much higher."
            )),
        ],
        keyPoints=[
            'Distance = Speed × Time; multiply km/h by 5/18 to get m/s.',
            'For equal distances at x and y, average speed = 2xy ÷ (x + y).',
            'Add speeds for opposite directions and subtract them for the same direction.',
            'A train passing a platform covers its own length plus the platform length.',
            'Stream speed = (downstream − upstream) ÷ 2.',
        ],
        challenges=[
            dict(id='challenge-aptitude-speed-distance-q1', kind='prediction', title='There and back',
                 prompt="A car travels from town A to town B at 45 km/h and returns along the same road at 30 km/h. What is its average speed for the round trip?",
                 options=['37.5 km/h', '36 km/h', '35 km/h', '40 km/h'], answer=1,
                 explanation="The distances are equal, so average speed = 2 × 45 × 30 ÷ (45 + 30) = 2,700 ÷ 75 = 36 km/h. Check with 90 km each way: 2 hours out and 3 hours back, so 180 km in 5 hours = 36 km/h. 37.5 km/h is the simple average of the two speeds, which would be right only if equal time were spent at each speed.",
                 hint="Average speed is total distance over total time; pick a convenient distance."),
            dict(id='challenge-aptitude-speed-distance-q2', kind='prediction', title='Passing a pole',
                 prompt="A train 280 m long passes a signal pole in 14 seconds. What is its speed in km/h?",
                 options=['20 km/h', '56 km/h', '72 km/h', '66 km/h'], answer=2,
                 explanation="Passing a pole, the train covers only its own length: 280 ÷ 14 = 20 m/s. Converting, 20 × 18/5 = 72 km/h. The option 20 km/h is the speed in m/s with the unit left unconverted.",
                 hint="Get the speed in m/s first, then convert."),
            dict(id='challenge-aptitude-speed-distance-q3', kind='prediction', title='Overtaking a walker',
                 prompt="A train 150 m long running at 63 km/h overtakes a man walking at 9 km/h in the same direction. How long does it take to pass him?",
                 options=['7.5 s', '8.57 s', '12 s', '10 s'], answer=3,
                 explanation="Same direction, so the relative speed = 63 − 9 = 54 km/h = 54 × 5/18 = 15 m/s. Time = 150 ÷ 15 = 10 seconds. 7.5 s adds the speeds, which applies only if the man were walking towards the train; 8.57 s ignores the man's speed altogether.",
                 hint="Decide whether the two speeds should be added or subtracted."),
            dict(id='challenge-aptitude-speed-distance-q4', kind='prediction', title='Speed of the stream',
                 prompt="A boat covers 48 km downstream in 3 hours and the same 48 km upstream in 4 hours. What is the speed of the stream?",
                 options=['2 km/h', '4 km/h', '14 km/h', '1 km/h'], answer=0,
                 explanation="Downstream speed = 48 ÷ 3 = 16 km/h and upstream speed = 48 ÷ 4 = 12 km/h. Stream speed = (16 − 12) ÷ 2 = 2 km/h. The option 4 km/h forgets to halve the difference, and 14 km/h is the boat's speed in still water.",
                 hint="Find both speeds first; the stream's speed is hidden in their difference."),
            dict(id='challenge-aptitude-speed-distance-q5', kind='prediction', title='Running late',
                 prompt="On a rainy morning Neha walks to the office at 4/5 of her normal pace and arrives 12 minutes later than she normally would. How long does her walk normally take?",
                 options=['60 minutes', '36 minutes', '48 minutes', '15 minutes'], answer=2,
                 explanation="For a fixed distance, time is inversely proportional to speed, so at 4/5 of the speed she takes 5/4 of the usual time. The extra 1/4 of the usual time equals 12 minutes, so the usual time is 48 minutes. 60 minutes is how long she took on the slow day, not her usual time.",
                 hint="At a fixed distance, a slower speed stretches the time by the reciprocal fraction."),
        ],
    ),
    dict(
        id='guide-aptitude-number-systems', kind='guide', track='aptitude', drill='number-systems',
        title='Number systems: divisibility, LCM and HCF', order=8,
        summary="Divisibility rules, prime factorisation and the LCM–HCF relationship answer most number questions without long division.",
        sections=[
            dict(title='Divisibility rules', text=(
                "These tests tell you whether a number divides exactly without doing the division.\n\n"
                "By 2: the last digit is even. By 5: the last digit is 0 or 5. By 10: the last digit is 0.\n"
                "By 4: the number formed by the last two digits is divisible by 4. By 8: the last three digits are divisible by 8.\n"
                "By 3: the digit sum is divisible by 3. By 9: the digit sum is divisible by 9.\n"
                "By 11: the difference between the sum of the digits in odd places and the sum in even places is 0 or a multiple of 11.\n\n"
                "For composite divisors, split them into co-prime factors and test each one. "
                "A number is divisible by 6 if it passes the tests for 2 and 3, by 12 if it passes 3 and 4, and by 15 if it passes 3 and 5. "
                "The factors must be co-prime: passing the tests for 2 and 4 does not prove divisibility by 8.\n\n"
                "Try 7,392. Its last three digits, 392, equal 8 × 49, so it is divisible by 8, and its digit sum is 21, so it is divisible by 3. "
                "Since 8 and 3 are co-prime, 7,392 is divisible by 24."
            )),
            dict(title='HCF and LCM', text=(
                "The HCF (highest common factor, also called the GCD) of two or more numbers is the largest number that divides all of them. "
                "The LCM (least common multiple) is the smallest number that all of them divide.\n\n"
                "The cleanest method is prime factorisation. Write each number as a product of prime powers. Then\n\n"
                "HCF = product of the common primes, each taken to its lowest power\n"
                "LCM = product of every prime that appears, each taken to its highest power\n\n"
                "For two numbers a and b there is a key link:\n\n"
                "HCF × LCM = a × b\n\n"
                "This finds a missing number or a missing LCM quickly. Be careful: it holds for exactly two numbers, not for three or more.\n\n"
                "A few checks catch errors. The HCF always divides the LCM. The HCF cannot exceed the smallest number, and the LCM cannot be smaller than the largest. "
                "Two numbers are co-prime when their HCF is 1, and then their LCM is simply their product. "
                "For large numbers, Euclid's method is faster: replace the larger number by its remainder on division by the smaller, and repeat until the remainder is 0."
            )),
            dict(title='Remainder patterns and fractions', text=(
                "Many questions disguise HCF and LCM as remainder problems.\n\n"
                "The largest number that divides a, b and c leaving the same remainder in each case is the HCF of the differences (b − a), (c − b) and (c − a).\n"
                "The largest number that divides a and b leaving remainders r1 and r2 is the HCF of (a − r1) and (b − r2), provided that HCF is bigger than both remainders.\n"
                "The smallest number, other than r itself, that leaves remainder r when divided by x, y and z (with r smaller than each) is LCM(x, y, z) + r.\n\n"
                "LCM also answers 'together again' questions: bells, lights or runners that repeat at different intervals next coincide after the LCM of those intervals.\n\n"
                "For fractions in lowest terms:\n\n"
                "HCF of fractions = HCF of numerators ÷ LCM of denominators\n"
                "LCM of fractions = LCM of numerators ÷ HCF of denominators\n\n"
                "For 3/8 and 9/20, the HCF is HCF(3, 9) ÷ LCM(8, 20) = 3/40 and the LCM is LCM(3, 9) ÷ HCF(8, 20) = 9/4. "
                "Check: 3/8 ÷ 3/40 = 5 and 9/20 ÷ 3/40 = 6, both whole numbers."
            )),
            dict(title='Worked examples', text=(
                "Example 1. Find the HCF and LCM of 132 and 198, and check them with the product rule.\n\n"
                "Step 1: Factorise. 132 = 2² × 3 × 11 and 198 = 2 × 3² × 11.\n"
                "Step 2: HCF = common primes at their lowest powers = 2 × 3 × 11 = 66.\n"
                "Step 3: LCM = every prime at its highest power = 2² × 3² × 11 = 396.\n"
                "Step 4: Check: 66 × 396 = 26,136 and 132 × 198 = 26,136. They match.\n\n"
                "Example 2. Find the largest number that divides 395, 538 and 720 leaving the same remainder in each case, and find that remainder.\n\n"
                "Step 1: The divisor must divide every difference: 538 − 395 = 143, 720 − 538 = 182 and 720 − 395 = 325.\n"
                "Step 2: Factorise: 143 = 11 × 13, 182 = 2 × 7 × 13 and 325 = 5² × 13.\n"
                "Step 3: The only common factor is 13, so the required number is 13.\n"
                "Step 4: 395 = 13 × 30 + 5, so the remainder is 5. Check: 538 = 13 × 41 + 5 and 720 = 13 × 55 + 5."
            )),
        ],
        keyPoints=[
            'Test composite divisors by splitting them into co-prime factors, such as 24 = 8 × 3.',
            'Divisibility by 11 uses the alternating sum of digits.',
            'HCF takes the lowest powers of common primes; LCM takes the highest powers of all primes.',
            'HCF × LCM equals the product, but only for two numbers.',
            'Same remainder from several numbers means: take the HCF of their differences.',
        ],
        challenges=[
            dict(id='challenge-aptitude-number-systems-q1', kind='prediction', title='Missing digit for 11',
                 prompt="What digit must replace * in 84*527 so that the number is divisible by 11?",
                 options=['7', '4', '6', '9'], answer=2,
                 explanation="Digits in odd places from the left (1st, 3rd, 5th): 8 + * + 2 = 10 + *. Digits in even places: 4 + 5 + 7 = 16. The difference (10 + *) − 16 = * − 6 must be 0 or a multiple of 11, and for a single digit only * = 6 works. Check: 846,527 = 11 × 76,957. The option 7 makes the plain digit sum 33, a multiple of 11, but the test for 11 uses the alternating sum, not the plain sum.",
                 hint="Compare the digits in alternate positions."),
            dict(id='challenge-aptitude-number-systems-q2', kind='prediction', title='The missing number',
                 prompt="The HCF of two numbers is 14 and their LCM is 840. If one number is 70, what is the other?",
                 options=['168', '120', '196', '84'], answer=0,
                 explanation="For two numbers, HCF × LCM = product, so the other number = 14 × 840 ÷ 70 = 11,760 ÷ 70 = 168. Check: 70 = 2 × 5 × 7 and 168 = 2³ × 3 × 7, so the HCF is 2 × 7 = 14 and the LCM is 2³ × 3 × 5 × 7 = 840. The option 120 is 840 ÷ 7, which uses the LCM alone and fails the HCF test: HCF(70, 120) is 10, not 14.",
                 hint="There is a direct link between HCF, LCM and the product of two numbers."),
            dict(id='challenge-aptitude-number-systems-q3', kind='prediction', title='Same remainder each time',
                 prompt="What is the smallest number greater than 4 that leaves a remainder of 4 when divided by each of 6, 9 and 15?",
                 options=['90', '94', '86', '814'], answer=1,
                 explanation="Such a number is 4 more than a common multiple of 6, 9 and 15. LCM(6, 9, 15) = 2 × 3² × 5 = 90, so the answer is 90 + 4 = 94. Check: 94 = 6 × 15 + 4 = 9 × 10 + 4 = 15 × 6 + 4. The option 814 adds 4 to the product 6 × 9 × 15 = 810, which is a common multiple but not the least one, and 90 forgets the remainder.",
                 hint="Start from the smallest number that all three divide exactly."),
            dict(id='challenge-aptitude-number-systems-q4', kind='prediction', title='HCF of fractions',
                 prompt="What is the HCF of 4/9, 10/21 and 8/15?",
                 options=['40/3', '2/3', '4/315', '2/315'], answer=3,
                 explanation="HCF of fractions = HCF of numerators ÷ LCM of denominators. HCF(4, 10, 8) = 2 and LCM(9, 21, 15) = 3² × 5 × 7 = 315, so the HCF is 2/315. Each fraction divided by 2/315 gives a whole number: 70, 75 and 84. The option 40/3 is the LCM of the fractions, the formula with HCF and LCM swapped.",
                 hint="For fractions, the numerators and the denominators get different operations."),
            dict(id='challenge-aptitude-number-systems-q5', kind='prediction', title='Bells together',
                 prompt="Three bells ring at intervals of 18, 24 and 40 seconds. They ring together at 9:00:00 am. When will they next ring together?",
                 options=['9:01:22 am', '9:12:00 am', '9:06:00 am'], answer=2,
                 explanation="18 = 2 × 3², 24 = 2³ × 3 and 40 = 2³ × 5, so LCM = 2³ × 3² × 5 = 360 seconds = 6 minutes, and they next ring together at 9:06:00 am. Adding the intervals (82 seconds, giving 9:01:22) has no meaning here, and 720 seconds (9:12:00) is a common multiple but not the least.",
                 hint="Look for the first moment that is a multiple of all three intervals."),
        ],
    ),
]
