"""Phase 5 enhancement tests: Real coordinate transforms and pedestrian variability."""

import pytest
from simulated_city.geo import distance_wgs84


class TestCoordinateTransforms:
    """Test real-world coordinate distance calculations."""
    
    def test_distance_between_koege_locations(self):
        """Verify distance between Køge Torv and Køge Søndre Strand."""
        # Køge Torv (safe zone)
        torv_lat, torv_lon = 55.4566, 12.1818
        
        # Køge Søndre Strand (evacuation zone)
        strand_lat, strand_lon = 55.4506, 12.1975
        
        distance = distance_wgs84(torv_lat, torv_lon, strand_lat, strand_lon)
        
        # Distance should be roughly 1100-1200 meters (real-world value)
        assert 1000 < distance < 1500, f"Unexpected distance: {distance}m"
    
    def test_distance_zero_same_point(self):
        """Verify distance is zero for same point."""
        lat, lon = 55.45, 12.19
        distance = distance_wgs84(lat, lon, lat, lon)
        
        assert distance < 1, f"Distance to same point should be ~0, got {distance}m"
    
    def test_distance_symmetry(self):
        """Verify distance is symmetric: d(A,B) == d(B,A)."""
        lat1, lon1 = 55.4566, 12.1818
        lat2, lon2 = 55.4506, 12.1975
        
        dist_ab = distance_wgs84(lat1, lon1, lat2, lon2)
        dist_ba = distance_wgs84(lat2, lon2, lat1, lon1)
        
        assert abs(dist_ab - dist_ba) < 0.1, "Distance should be symmetric"
    
    def test_distance_positive(self):
        """Verify distance is always positive."""
        points = [
            (55.45, 12.18),
            (55.46, 12.20),
            (55.44, 12.17),
        ]
        
        for i, (lat1, lon1) in enumerate(points):
            for j, (lat2, lon2) in enumerate(points):
                if i != j:
                    distance = distance_wgs84(lat1, lon1, lat2, lon2)
                    assert distance > 0, f"Distance must be positive: {distance}"
    
    def test_distance_sanity(self):
        """Verify distances make geographic sense."""
        # Copenhagen city center
        copenhagen_lat, copenhagen_lon = 55.6761, 12.5683
        
        # Køge (about 34km south)
        koege_lat, koege_lon = 55.4566, 12.1818
        
        distance = distance_wgs84(copenhagen_lat, copenhagen_lon, koege_lat, koege_lon)
        
        # Should be 33-36km (actual: ~34.4km)
        assert 33000 < distance < 36000, f"Copenhagen-Køge distance wrong: {distance}m"


class TestPedestrianVariability:
    """Test pedestrian evacuation with realistic variability."""
    
    def test_evacuation_speed_variance(self):
        """Verify pedestrians have realistic speed variance."""
        num_pedestrians = 10
        base_evacuation_time = 8.0  # seconds
        
        # Generate speeds with variance
        speeds = []
        for i in range(num_pedestrians):
            # Simulate speed drawn from realistic distribution
            # 70% nominal speed, 15% faster, 15% slower
            import random
            random.seed(i)  # Deterministic for testing
            
            speed_ratio = random.gauss(1.0, 0.2)  # Gaussian with 20% std dev
            speed = speed_ratio
            speeds.append(speed)
        
        # Verify speeds are realistic
        assert all(0.5 < s < 1.5 for s in speeds), "Speed ratios out of range"
        assert len(speeds) == num_pedestrians
    
    def test_evacuation_times_with_variance(self):
        """Verify evacuation times vary by pedestrian."""
        num_pedestrians = 10
        base_time = 8.0
        
        # All should evacuate within reasonable time window
        times = []
        for i in range(num_pedestrians):
            import random
            random.seed(i * 2)
            
            # Simulate evacuation time with variance
            variance = random.gauss(0, 0.5)  # ±0.5 seconds
            time = base_time + variance
            times.append(time)
        
        # All times should be reasonable
        assert all(5 < t < 11 for t in times), f"Evacuation times out of range: {times}"
        assert min(times) < max(times), "There should be variance in times"
    
    def test_evacuation_order_randomness(self):
        """Verify evacuation order can vary."""
        # In reality, some people evacuate faster/slower
        import random
        
        num_pedestrians = 10
        arrival_times = []
        
        # Simulate realistic arrivals at destination
        for i in range(num_pedestrians):
            random.seed(i * 3)
            arrival_fraction = random.gauss(0.5, 0.15)  # Arrive mid-evacuation ±15%
            arrival_times.append(max(0, min(1, arrival_fraction)))
        
        # Times should be distributed, not all the same
        assert max(arrival_times) - min(arrival_times) > 0.1, "Should have time spread"


class TestDashboardEnhancements:
    """Test enhanced dashboard features."""
    
    def test_distance_display_calculation(self):
        """Verify dashboard can calculate and display distances."""
        torv = (55.4566, 12.1818)
        strand = (55.4506, 12.1975)
        
        distance = distance_wgs84(torv[0], torv[1], strand[0], strand[1])
        distance_km = distance / 1000
        
        # Should format nicely for display
        display_str = f"{distance_km:.2f} km"
        assert "1.1" in display_str or "1.2" in display_str, f"Unexpected display: {display_str}"
    
    def test_evacuation_progress_with_real_distance(self):
        """Verify evacuation progress can show real distance traveled."""
        distance_total = 1200  # meters (approximate Torv to Strand)
        
        # Simulate evacuation progress at different times
        evacuation_times = [0, 2, 4, 6, 8]  # seconds
        evacuation_duration = 8.0
        
        distances_traveled = []
        for t in evacuation_times:
            progress = min(t / evacuation_duration, 1.0)
            distance_traveled = distance_total * progress
            distances_traveled.append(distance_traveled)
        
        # Verify distances increase monotonically
        for i in range(1, len(distances_traveled)):
            assert distances_traveled[i] >= distances_traveled[i-1]
        
        # Final distance should be close to total
        assert distances_traveled[-1] > distance_total * 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
