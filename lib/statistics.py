from pandas import array


class Statistics:
    def __init__(self, step_days: array, step_goal: int=5000) -> None:
        ## Only allow initialization with a list of days
        ## Process all immediately
        if step_days is None or len(step_days) <=0:
            raise ValueError("Cannot analyze statistics without any days")
        self.days = step_days
        self.step_goal = step_goal
        self.months = {}
        self.years = {}
        self.__calculate_sums__()

    def calculate_stats(self):
        '''
        Method for generating aggregate statistics and assigning daily ranks
        '''
        self.__calculate_sums__()

    def get_most_recent_days(self, day_count=10):
        count = min(day_count, len(self.days))
        return self.days[-count:]

    def find_maximum_streak(self):
        def is_bigger_streak(current_streak, max_streak, current_steps, streak_steps):
            if current_streak > max_streak:
                return True
            if current_streak == max_streak and current_steps > streak_steps:
                return True
            return False
        max_streak = 0
        streak_steps = 0
        streak_end = ''
        current_streak = 0
        current_steps = 0

        for i in range(0, len(self.days)):
            day_steps = int(self.days[i].steps)
            if day_steps >= self.step_goal:
                current_streak += 1
                current_steps += day_steps
                if is_bigger_streak(current_streak, max_streak, current_steps, streak_steps):
                    max_streak = current_streak
                    streak_steps = current_steps
                    streak_end = self.days[i].date if i > 0 else ''
            else:	
                current_streak = 0
                current_steps = 0
        return (max_streak, streak_steps, streak_end)

    def __calculate_sums__(self):
        for day in self.days:
            year, month = (day.date.year, day.date.month)
            goal_met = day.steps > self.step_goal
            self.__add_to_stats_dict__(self.years, day.steps, year, goal_met)
            self.__add_to_stats_dict__(self.months, day.steps, f"{year}-{month}", goal_met)
    
    def __add_to_stats_dict__(self, stats_dict, daily_step_count, key, goal_met):
        if key not in stats_dict:
            stats_dict[key]={"steps": 0, "days": 0, "goal_days": 0}
        
        stats_dict[key]["steps"] += daily_step_count
        stats_dict[key]["days"] += 1
        if goal_met:
            stats_dict[key]["goal_days"] += 1

    def __repr__(self) -> str:
        return "repr NOT YET IMPLEMENTED"

    def __str__(self) -> str:
        return "str NOT YET IMPLEMENTED"
