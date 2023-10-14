import datetime as dt

class Day:
    def __init__(self, val_dict) -> None:
        self.steps = int(val_dict["steps"])
        self.date = dt.datetime.strptime(val_dict["date"], "%Y-%m-%d").date()
        self.all_time_rank = -1
        self.top_percentile = -1
    
    def __gt__(self, other):
        return self.date > other.date

    def __lt__(self, other):
        return self.date < other.date

    def __eq__(self, other):
        ## If two dates are equal one should be discarded else it will double count steps for stat calculation
        return not self.date < other.date and not self.date > other.date and self.steps == other.steps

    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return f"{self.date}: {self.steps:,} steps, which ranks {self.__make_ordinal__()} all-time and is top {self.top_percentile:.2f}%"
    
    def __make_ordinal__(self) -> str:
        rank = self.all_time_rank
        return "%d%s" % (rank,"tsnrhtdd"[(rank//10%10!=1)*(rank%10<4)*rank%10::4])
