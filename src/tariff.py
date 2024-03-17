from datetime import datetime, time


class Tariff:
    peak_rate: float
    off_peak_rate: float
    off_peak_times: list[tuple[int]]

    def __init__(self, peak: float, off_peak: float) -> None:
        self.peak_rate = peak
        self.off_peak_rate = off_peak
        self.off_peak_times = [(0, 5), (13, 16), (20, 22)]

    def off_peak(self, start: datetime) -> bool:
        t = start.time()
        for time_range in self.off_peak_times:
            lower = time(time_range[0])
            higher = time(time_range[1])
            if t >= lower and t < higher:
                return True
        return False

    def peak(self, start: datetime) -> bool:
        return not self.off_peak(start)

    def evening_peak(self, start: datetime) -> bool:
        return start >= time(16) and start < time(19)

    def cost(self, consumption: float, peak: bool) -> float:
        if peak:
            rate = self.peak_rate
        else:
            rate = self.off_peak_rate
        return consumption * rate