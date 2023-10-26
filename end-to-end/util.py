def make_timestamp(total_time, ref):
    hh = int((total_time + ref) / 3600)
    mm = int((total_time + ref) / 60) % 60
    ss = int((total_time + ref) % 60)
    mmm = int((total_time + ref) % 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{mmm:03d}"
