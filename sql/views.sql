-- convenience views
USE assignment_2;

CREATE OR REPLACE VIEW v_trip_timebands AS
SELECT
  trip_id, taxi_id, call_type, day_type, start_ts, duration_s, distance_m,
  CASE
    WHEN HOUR(start_ts) < 6  THEN '00–06'
    WHEN HOUR(start_ts) < 12 THEN '06–12'
    WHEN HOUR(start_ts) < 18 THEN '12–18'
    ELSE '18–24'
  END AS time_band
FROM trips;

CREATE OR REPLACE VIEW v_midnight_crossers AS
SELECT
  trip_id, taxi_id, start_ts,
  (start_ts + INTERVAL GREATEST(points_count-1,0)*15 SECOND) AS end_ts
FROM trips
WHERE DATE(start_ts) <> DATE(start_ts + INTERVAL GREATEST(points_count-1,0)*15 SECOND);
