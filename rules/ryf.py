from random import randint

class RyF:
    def attr_skill_roll(self, dice_index):
        result = []

        all_rolls = []
        roll_result = self.dices()
        all_rolls.append(roll_result)

        objective = sorted(roll_result)[dice_index]

        if objective == 1:
            if dice_index < 2:
                next_dice = sorted(roll_result)[dice_index + 1]
                if next_dice <= 5:
                    result.append(all_rolls)
                    result.append(objective)
                    result.append(next_dice)
                    return result
            else:
                result.append(all_rolls)
                result.append(objective)
                return result
        
        total_roll = objective

        while objective == 10:
            roll_result = self.dices()
            all_rolls.append(roll_result)
            objective = sorted(roll_result)[dice_index]

            total_roll = total_roll + objective
        
        result.append(all_rolls)
        result.append(total_roll)

        return result

    def effect_roll(self, dice_amount):
        result = []
        
        roll_result = self.dices(6, dice_amount)

        exploding_dices = roll_result.count(6)

        while exploding_dices > 0:
            exploding_roll_result = self.dices(6, exploding_dices)
            roll_result.extend(exploding_roll_result)
            exploding_dices = exploding_roll_result.count(6)

        total_roll = 0
        for roll_value in roll_result:
            total_roll = total_roll + roll_value
        
        result.append(roll_result)
        result.append(total_roll)
        return result

    def dices(self, dicevalue=10, amount=3):
        min = 1
        max = dicevalue

        result = []

        for _ in range(amount):
            result.append(randint(min, max))

        return result