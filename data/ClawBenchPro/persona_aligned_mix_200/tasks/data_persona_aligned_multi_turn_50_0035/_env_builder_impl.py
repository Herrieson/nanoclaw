import os
import argparse
import json

def build_turn_1():
    os.makedirs("cluster_logs", exist_ok=True)
    os.makedirs("heap_dumps", exist_ok=True)
    os.makedirs("query_plans", exist_ok=True)

    # 1. Mock cluster logs
    log_content_1 = """[2023-10-25 10:01:12] [INFO] Node-01 started successfully.
[2023-10-25 10:05:00] [INFO] Worker-1 processing partition A.
[2023-10-25 10:08:11] [INFO] Worker-1 finished."""
    
    log_content_2 = """[2023-10-25 10:01:15] [INFO] Node-02 started successfully.
[2023-10-25 10:06:22] [WARN] Memory usage exceeding 80% on Node-02.
[2023-10-25 10:07:05] [ERROR] Worker-7 encountered unhandled exception!
[2023-10-25 10:07:06] [FATAL] OOM Core Dumped for Thread-404. JVM Halted."""
    
    with open("cluster_logs/node_01.log", "w") as f: f.write(log_content_1)
    with open("cluster_logs/node_02.log", "w") as f: f.write(log_content_2)

    # 2. Mock heap dumps
    dump_trap = """Thread-202 (WAITING)
    at com.graphdb.storage.DiskReader.read(DiskReader.java:55)
    at com.graphdb.core.Vertex.load(Vertex.java:102)"""
    
    dump_fatal = """Thread-404 (RUNNABLE)
java.lang.OutOfMemoryError: Java heap space
    at java.util.ArrayList.grow(ArrayList.java:260)
    at com.graphdb.core.Traversal.expand(Traversal.java:142)
    at com.graphdb.core.EdgeIterator.next(EdgeIterator.java:88)
    at com.graphdb.core.Traversal.expand(Traversal.java:144)  <-- Cyclic Loop Detected
Local Variable Context:
    currentVertex = V[8837192] (Label: PERSON)
    edgeType = FOLLOWS
    depth = 12
    metadata = { is_supernode: true, degree: 14509211 }"""
    
    with open("heap_dumps/thread_202_dump.txt", "w") as f: f.write(dump_trap)
    with open("heap_dumps/thread_404_dump.txt", "w") as f: f.write(dump_fatal)

    # 3. Mock query plans
    plan_safe = {
        "query_id": "q-100",
        "entry_points": ["V[1002]", "V[1003]"],
        "steps": [
            {"type": "OUT", "edge": "FOLLOWS", "max_depth": 2},
            {"type": "FILTER", "condition": "age > 20"}
        ]
    }
    plan_fatal = {
        "query_id": "q-991",
        "entry_points": ["V[8837192]"],
        "steps": [
            {"type": "BOTH", "edge": "FOLLOWS", "max_depth": 15},
            {"type": "AGGREGATE", "function": "COUNT"}
        ]
    }
    plan_trap = {
        "query_id": "q-992",
        "entry_points": ["V[8837192]"],
        "steps": [
            {"type": "OUT", "edge": "PURCHASED", "max_depth": 1}
        ]
    }
    
    with open("query_plans/plan_100.json", "w") as f: json.dump(plan_safe, f, indent=2)
    with open("query_plans/plan_991.json", "w") as f: json.dump(plan_fatal, f, indent=2)
    with open("query_plans/plan_992.json", "w") as f: json.dump(plan_trap, f, indent=2)

def build_turn_2():
    os.makedirs("incoming_queries", exist_ok=True)
    
    incoming_batch = [
        {
            "req_id": "req-001",
            "start_vertex": "V[1055]",
            "traversal": {"direction": "OUT", "edge_label": "FOLLOWS", "depth": 3}
        },
        {
            "req_id": "req-002",
            "start_vertex": "V[8837192]",
            "traversal": {"direction": "OUT", "edge_label": "FOLLOWS", "depth": 10}
        },
        {
            "req_id": "req-003",
            "start_vertex": "V[9999999]",
            "traversal": {"direction": "BOTH", "edge_label": "FOLLOWS", "depth": 15}
        },
        {
            "req_id": "req-004",
            "start_vertex": "V[8837192]",
            "traversal": {"direction": "IN", "edge_label": "PURCHASED", "depth": 1}
        }
    ]
    
    with open("incoming_queries/batch_1.json", "w") as f:
        json.dump(incoming_batch, f, indent=2)

def build_turn_3():
    os.makedirs("hotfix_patches", exist_ok=True)
    
    patch_a = """--- a/conf/jvm_options.sh
+++ b/conf/jvm_options.sh
@@ -10,3 +10,3 @@
-Xmx128G
+Xmx256G
-XX:+UseG1GC
"""

    patch_b = """--- a/src/main/java/com/graphdb/core/Traversal.java
+++ b/src/main/java/com/graphdb/core/Traversal.java
@@ -140,6 +140,10 @@
     public void expand(Vertex currentVertex, String edgeType, int depth) {
+        if (depth > 5 && currentVertex.getDegree() > 10000000) {
+             throw new QueryLimitException("Supernode expansion aborted to prevent OOM.");
+        }
         for (Edge e : currentVertex.getEdges(edgeType)) {
             Vertex next = e.getTarget();
             expand(next, edgeType, depth + 1);
         }
     }
"""

    patch_c = """--- a/src/main/java/com/graphdb/core/Traversal.java
+++ b/src/main/java/com/graphdb/core/Traversal.java
@@ -139,7 +139,12 @@
-    public void expand(Vertex currentVertex, String edgeType, int depth) {
+    public void expand(Vertex currentVertex, String edgeType, int depth, Set<VertexId> visited) {
+        if (visited.contains(currentVertex.getId())) {
+            return; // Break cyclic reference
+        }
+        visited.add(currentVertex.getId());
         for (Edge e : currentVertex.getEdges(edgeType)) {
             Vertex next = e.getTarget();
-            expand(next, edgeType, depth + 1);
+            expand(next, edgeType, depth + 1, visited);
         }
+        visited.remove(currentVertex.getId());
     }
"""
    
    with open("hotfix_patches/PR_101_increase_heap.diff", "w") as f: f.write(patch_a)
    with open("hotfix_patches/PR_102_hard_limit.diff", "w") as f: f.write(patch_b)
    with open("hotfix_patches/PR_103_cycle_detection.diff", "w") as f: f.write(patch_c)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
