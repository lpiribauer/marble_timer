import colorsys


class Marble:

    def __init__(self, id, color):
        self.color = color
        self.lap_times = []
        self.id = id
        self.name =''

    def get_last_lap_time(self):
        if len(self.lap_times) > 1:
            return self.lap_times[len(self.lap_times) - 1] - self.lap_times[len(self.lap_times) - 2]
        else:
            return -1

    def get_number_of_laps(self):
        if self.lap_times:
            return len(self.lap_times)
        else:
            return 0

    def get_overall_time(self):
        if self.lap_times:
            return self.lap_times[len(self.lap_times) - 1]
        else:
            return -1

    def get_time_difference(self, time_first, laps_first):
        lap_diff = laps_first - self.get_number_of_laps()
        if lap_diff > 0:
            return "+ " + str(lap_diff) + " Runde"
        else:
            return self.get_overall_time() - time_first

    def get_best_lap_time(self):
        best_lap_time = 100000
        for i in range(len(self.lap_times)):
            if i > 0:
                lap_time = self.lap_times[i] - self.lap_times[i - 1]
                if lap_time < best_lap_time:
                    best_lap_time = lap_time
        return best_lap_time

    def reset_marble(self):
        self.lap_times = []

    def get_display_color(self):
        return (self.color[1], self.color[2], self.color[0])




