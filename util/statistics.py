class Statistics:
    def __init__(self, step_days: list, step_goal: int=5000) -> None:
        ## Only allow initialization with a list of days
        ## Process all immediately
        if step_days is None or len(step_days) <=0:
            raise ValueError("Cannot analyze statistics without any days")
        self.days = step_days
        self.step_goal = step_goal
        self.all_time_steps = 0
        self.all_time_average = 0
        self.months = {}
        self.years = {}
        self.calculate_stats()

    def calculate_stats(self):
        '''
        Method for generating aggregate statistics and assigning daily ranks
        '''
        self.__calculate_sums__()
        self.__calculate_averages__() 
        self.__calculate_percent_at_goal__()
        self.__calculate_daily_rank__()


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
            self.all_time_steps += day.steps
            year, month = (day.date.year, day.date.month)
            goal_met = day.steps >= self.step_goal
            self.__add_to_stats_dict__(self.years, day.steps, f"{year}", goal_met)
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

    def __calculate_percent_at_goal__(self):
        for month in self.months:
            self.months[month]["goal_percent"] = float(self.months[month]["goal_days"]/self.months[month]["days"] * 100)

        for year in self.years:
            self.years[year]["goal_percent"] = float(self.years[year]["goal_days"]/self.years[year]["days"] * 100)

    def __calculate_averages__(self):
        for month in self.months:
            self.months[month]["daily_average_steps"] = int(self.months[month]["steps"]/self.months[month]["days"])

        for year in self.years:
            self.years[year]["daily_average_steps"] = int(self.years[year]["steps"]/self.years[year]["days"])

        self.all_time_average = self.all_time_steps // len(self.days)

    def __calculate_daily_rank__(self):
        step_sorted = sorted(self.days, key=lambda k: k.steps, reverse=True)
        for i in range(0, len(step_sorted)):
            step_sorted[i].all_time_rank = i+1
            step_sorted[i].top_percentile = i/len(step_sorted) * 100
