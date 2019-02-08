from ryf import RyF

class DxD(RyF):
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

        pair_dice = 1
        if(dice_index < 2):
            pair_dice = sorted(roll_result)[dice_index + 1]
        else:
            pair_dice = sorted(roll_result)[dice_index - 1]

        while pair_dice == objective:
            roll_result = self.dices()
            all_rolls.append(roll_result)
            objective = sorted(roll_result)[dice_index]
            
            total_roll = total_roll + objective

            if(dice_index < 2):
                pair_dice = sorted(roll_result)[dice_index + 1]
            else:
                pair_dice = sorted(roll_result)[dice_index - 1]
        
        result.append(all_rolls)
        result.append(total_roll)

        return result