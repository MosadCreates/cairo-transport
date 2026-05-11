"""
test_algorithms.py — CSE112 Project
Unit tests for the Cairo Transportation Network Optimization System.
"""

import unittest
import math

from core.graph import build_cairo_graph
from algorithms.shortest_path import shortest_path, astar, time_dependent_dijkstra
from algorithms.mst import kruskal_mst
from algorithms.dp_solutions import bus_fleet_allocation, road_maintenance_knapsack, metro_headway_optimization
from algorithms.greedy import traffic_signal_optimization, emergency_preemption
from utils.transit_network import optimize_transit_route, analyze_transfer_points

class TestAlgorithms(unittest.TestCase):

    def setUp(self):
        self.g_full = build_cairo_graph(include_potential=True)
        self.g_existing = build_cairo_graph(include_potential=False)

    def test_graph_building(self):
        """Test if graph builds correctly with appropriate nodes and edges."""
        self.assertGreater(len(self.g_full.nodes), 0, "Graph should have nodes.")
        self.assertGreater(len(self.g_full.all_edges()), len(self.g_existing.all_edges()), 
                           "Full graph should have more edges than existing graph.")

    def test_dijkstra_shortest_path(self):
        """Test standard Dijkstra route planning."""
        dist, path = shortest_path(self.g_existing, 4, 3) # New Cairo to Downtown
        self.assertTrue(len(path) >= 2, "Path should contain at least start and end nodes.")
        self.assertEqual(path[0], 4, "Path should start at node 4.")
        self.assertEqual(path[-1], 3, "Path should end at node 3.")
        self.assertGreater(dist, 0, "Distance should be positive.")

    def test_astar_routing(self):
        """Test A* search for emergency vehicles."""
        time, path = astar(self.g_existing, 8, "F9") # Giza to Qasr El Aini
        self.assertTrue(len(path) >= 2, "Path should contain at least start and end nodes.")
        self.assertEqual(path[-1], "F9", "Path should reach the hospital.")
        self.assertGreater(time, 0, "Travel time should be positive.")

    def test_kruskal_mst(self):
        """Test Kruskal's MST for network design."""
        mst_edges, cost, dist = kruskal_mst(self.g_full)
        self.assertEqual(len(mst_edges), 20, 
                         "MST should have 20 edges (4 nodes are isolated in the dataset).")
        
        # Verify critical nodes are in the MST
        nodes_in_mst = set()
        for u, v, _, _ in mst_edges:
            nodes_in_mst.add(u)
            nodes_in_mst.add(v)
            
        self.assertIn("F9", nodes_in_mst, "Hospital F9 must be in MST.")
        self.assertIn("F10", nodes_in_mst, "Hospital F10 must be in MST.")
        self.assertIn(13, nodes_in_mst, "Capital 13 must be in MST.")

    def test_dp_bus_allocation(self):
        """Test 0/1 Knapsack for bus fleet allocation."""
        alloc, total_pass, _ = bus_fleet_allocation(total_buses=100)
        self.assertLessEqual(sum(alloc.values()), 100, "Should not allocate more than total available buses.")
        self.assertGreater(total_pass, 0, "Should serve a positive number of passengers.")

    def test_greedy_traffic_signals(self):
        """Test greedy allocation for traffic signals."""
        signals = traffic_signal_optimization("morning")
        self.assertGreater(len(signals), 0, "Should optimize at least one intersection.")
        # Check that green times sum to cycle time for the first intersection
        first_sig = signals[0]
        total_green = sum(g for _, _, g in first_sig["arms"])
        self.assertEqual(total_green, 90, "Total green time must equal the 90s cycle.")

    def test_transit_routing(self):
        """Test multimodal transit routing."""
        time, path = optimize_transit_route(1, 9)
        self.assertGreater(time, 0, "Transit time should be positive.")
        self.assertGreater(len(path), 0, "Should find a valid transit path.")

    def test_transfer_hubs(self):
        """Test transfer point analysis."""
        hubs = analyze_transfer_points()
        self.assertGreater(len(hubs), 0, "Should identify at least one transfer hub.")
        self.assertTrue("hub_score" in hubs[0], "Hubs should be scored.")

if __name__ == "__main__":
    unittest.main()
