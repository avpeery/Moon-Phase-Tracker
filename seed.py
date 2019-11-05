from skyfield import api, almanac


def load_moon_phases():
    ts = api.load.timescale(builtin=True)
    e = api.load('de421.bsp')

    t0 = ts.utc(2000, 1, 1)
    t1 = ts.utc(2050, 12, 31)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

    print(t.utc_iso())
    print(y)
    print([almanac.MOON_PHASES[yi] for yi in y])

load_moon_phases()

# t2 = ts.utc(2019, 1, 1)
# t3 = ts.utc(2019, 12, 30)
# t5, y1 = almanac.find_discrete(t2, t3, almanac.moon_phases(e))

# print(t5.utc_iso())
# print(y1)
# print([almanac.MOON_PHASES[y1i] for y1i in y1])