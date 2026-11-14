"""Unit tests for vis-design. Run: python3 -m unittest discover -s scripts/tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

from visdesign import vocab, shape, store, catalog, scoring  # noqa: E402
from visdesign.records import validate, validate_composition, key  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class TestVocabShape(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(vocab.band_for(1), "one")
        self.assertEqual(vocab.band_for(7), "few")
        self.assertEqual(vocab.band_for(8), "some")
        self.assertEqual(vocab.band_for(42), "many")
        self.assertEqual(vocab.band_for(585), "huge")

    def test_signature_ignores_roles_and_grain(self):
        a = {"dataset_type": "table", "keys": [{"role": "time", "type": "temporal", "cardinality": 14, "grain": "year"},
                                                {"role": "category", "type": "categorical", "cardinality": 42}],
             "values": [{"role": "measure", "type": "quantitative", "semantics": "count"}]}
        b = {"dataset_type": "table", "keys": [{"role": "location", "type": "categorical", "cardinality": "many"},
                                                {"role": "period", "type": "temporal", "cardinality": "some"}],
             "values": [{"role": "x", "type": "quantitative", "semantics": "count"}]}
        self.assertEqual(shape.signature(a), shape.signature(b))
        self.assertEqual(shape.signature(a), "table|k:categorical:many+k:temporal:some|v:quantitative:count")

    def test_similarity_orders(self):
        q = {"dataset_type": "table", "keys": [{"type": "temporal", "cardinality": "some"}, {"type": "categorical", "cardinality": "many"}],
             "values": [{"type": "quantitative", "semantics": "count"}]}
        same, _ = shape.shape_similarity(q, q)
        close, _ = shape.shape_similarity(q, {"dataset_type": "table", "keys": [{"type": "temporal", "cardinality": "few"}, {"type": "categorical", "cardinality": "many"}], "values": [{"type": "quantitative", "semantics": "count"}]})
        far, _ = shape.shape_similarity(q, {"dataset_type": "table", "keys": [], "values": [{"type": "quantitative"}, {"type": "quantitative"}]})
        self.assertEqual(same, 1.0)
        self.assertGreater(same, close)
        self.assertGreater(close, far)


class TestSeeds(unittest.TestCase):
    def test_every_seed_validates_and_keys_unique(self):
        seeds = store.load_dir(store.seed_dir(), "seed")
        self.assertGreaterEqual(len(seeds), 30)
        keys = set()
        for r in seeds:
            errs = validate(r, set(catalog.load()), set(catalog.archetypes()), set(catalog.profiles()))
            self.assertEqual(errs, [], f"{r['id']}: {errs}")
            k = key(r)
            self.assertNotIn(k, keys, f"duplicate key {k}")
            keys.add(k)

    def test_every_archetype_has_a_seed(self):
        seeds = store.load_dir(store.seed_dir(), "seed")
        have = {r["problem"]["archetype"] for r in seeds}
        self.assertEqual(set(catalog.archetypes()) - have, set())

    def test_build_index_check_passes(self):
        rc, out, err = run("build_index.py", "--check")
        self.assertEqual(rc, 0, out + err)


class TestComposition(unittest.TestCase):
    def _comp(self, **over):
        comp = {"type": "juxtapose", "relation": "multiform", "data_sharing": "all",
                "encoding_sharing": "different",
                "views": [{"id": "a", "idiom": "scatterplot", "role": "focus"},
                          {"id": "b", "idiom": "bar_chart", "role": "context"}],
                "links": [{"from": "a", "to": "b", "type": "filter"},
                          {"from": "b", "to": "a", "type": "highlight"}]}
        comp.update(over)
        return comp

    def test_absent_and_valid(self):
        self.assertEqual(validate_composition(None), [])
        self.assertEqual(validate_composition(self._comp(), set(catalog.load())), [])

    def test_unknown_terms(self):
        errs = validate_composition(self._comp(type="side-by-side", relation="friends"))
        self.assertTrue(any("view_compositions" in e for e in errs), errs)
        self.assertTrue(any("view_relations" in e for e in errs), errs)

    def test_link_to_missing_view_and_single_view(self):
        errs = validate_composition(self._comp(links=[{"from": "a", "to": "zzz", "type": "highlight"}]))
        self.assertTrue(any("'zzz' is not a declared view" in e for e in errs), errs)
        errs = validate_composition(self._comp(views=[{"id": "a", "idiom": "scatterplot", "role": "focus"}], links=[]))
        self.assertTrue(any("at least two views" in e for e in errs), errs)
        errs = validate_composition(self._comp(), {"bar_chart"})
        self.assertTrue(any("not in catalog" in e for e in errs), errs)

    def test_seeds_with_composition_exist(self):
        seeds = store.load_dir(store.seed_dir(), "seed")
        with_comp = [r for r in seeds if r["solution"].get("composition")]
        self.assertGreaterEqual(len(with_comp), 3)
        for r in with_comp:
            self.assertEqual(validate_composition(r["solution"]["composition"], set(catalog.load())), [], r["id"])


class TestMatching(unittest.TestCase):
    def _answers(self, archetype, profile, mode, keys, values, tasks):
        return {"problem": {"archetype": archetype, "mode": mode, "statement": "q"},
                "user": {"profile": profile, "modifiers": []},
                "tasks": {"why": {"goal": "discover", "search": "browse", "query": "compare"}, "low_level": tasks, "temporal": [], "shneiderman": []},
                "data": {"dataset_type": "table", "keys": keys, "values": values, "items": "small"}, "constraints": []}

    def test_exact_seed_match(self):
        a = self._answers("trend-many-series", "domain-expert", "analysis",
                          [{"role": "time", "type": "temporal", "cardinality": 14, "grain": "year"}, {"role": "category", "type": "categorical", "cardinality": 42}],
                          [{"role": "measure", "type": "quantitative", "semantics": "count"}],
                          ["compare", "find-anomalies"])
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "answers.json")
            json.dump(a, open(p, "w"))
            rc, out, err = run("match_decision.py", p, "--project-dir", os.path.join(td, "store"))
            self.assertEqual(rc, 0, err)
            d = json.loads(out)
            self.assertEqual(d["tier"], "EXACT")
            self.assertEqual(d["best"]["id"], "trend-many-series--heatmap-key-x-time")
            self.assertEqual(d["defaults"]["idiom"], "heatmap")

    def test_project_record_shadows_seed(self):
        a = self._answers("trend-many-series", "domain-expert", "analysis",
                          [{"role": "time", "type": "temporal", "cardinality": "some"}, {"role": "category", "type": "categorical", "cardinality": "many"}],
                          [{"role": "measure", "type": "quantitative", "semantics": "count"}], ["compare"])
        with tempfile.TemporaryDirectory() as td:
            storedir = os.path.join(td, "store")
            # build a project record from the seed with a different idiom
            seed = next(r for r in store.load_dir(store.seed_dir(), "seed") if r["id"] == "trend-many-series--heatmap-key-x-time")
            rec = {k: v for k, v in seed.items() if not k.startswith("_")}
            rec["solution"] = dict(rec["solution"], idiom="small_multiples", family="small-multiples")
            rec["title"] = "project override"
            rp = os.path.join(td, "rec.json")
            json.dump(rec, open(rp, "w"), default=str)
            rc, out, err = run("record_decision.py", rp, "--project-dir", storedir)
            self.assertEqual(rc, 0, out + err)
            rid = json.loads(out)["id"]
            self.assertTrue(rid.startswith("p-trend-many-series"))
            p = os.path.join(td, "answers.json")
            json.dump(a, open(p, "w"))
            rc, out, err = run("match_decision.py", p, "--project-dir", storedir)
            d = json.loads(out)
            self.assertEqual(d["tier"], "EXACT")
            self.assertEqual(d["best"]["id"], rid)
            self.assertEqual(d["defaults"]["idiom"], "small_multiples")
            # touch bumps usage
            rc, out, err = run("record_decision.py", "--touch", rid, "--project-dir", storedir)
            self.assertIn("times_used", out)

    def test_constraint_excludes(self):
        a = self._answers("multivariate-relationships", "executive", "explanatory",
                          [{"role": "category", "type": "categorical", "cardinality": "some"}],
                          [{"role": "measure", "type": "quantitative", "semantics": "score"}, {"role": "measure2", "type": "quantitative", "semantics": "score"}, {"role": "weight", "type": "quantitative", "semantics": "score"}],
                          ["compare"])
        a["constraints"] = ["static-only"]
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "answers.json")
            json.dump(a, open(p, "w"))
            rc, out, err = run("match_decision.py", p, "--project-dir", os.path.join(td, "s"))
            d = json.loads(out)
            self.assertIn("multivariate-relationships--parallel-coordinates-analyst", [e["id"] for e in d["excluded"]])
            self.assertEqual(d["best"]["id"], "multivariate-relationships--heatmap-items-by-measures")

    def test_catalog_candidates_respect_archetype(self):
        q = {"problem": {"archetype": "part-to-whole-single", "mode": "explanatory"}, "user": {"profile": "general-public"},
             "data": {"dataset_type": "table", "keys": [{"type": "categorical", "cardinality": 4}], "values": [{"type": "quantitative", "semantics": "share"}]},
             "constraints": []}
        c = catalog.rank_candidates(q)
        self.assertEqual(c[0]["idiom"], "bar_chart")
        self.assertTrue(any(x["idiom"] == "pie_chart" and x["notes"] for x in c))


class TestProfileData(unittest.TestCase):
    def test_events_fixture(self):
        rc, out, err = run("profile_data.py", os.path.join(FIX, "events.csv"))
        self.assertEqual(rc, 0, err)
        d = json.loads(out)
        cols = {c["name"]: c for c in d["columns"]}
        self.assertEqual(cols["EVENT_DATE"]["inferred_type"], "temporal")
        self.assertEqual(cols["EVENT_DATE"]["date_format"], "%d/%m/%Y")
        self.assertEqual(cols["REGION_CODE"]["role_suggestion"], "identifier")
        self.assertEqual(cols["CAUSE"]["band"], "few")
        self.assertEqual(cols["AREA_HA"]["inferred_type"], "quantitative")
        self.assertTrue(any("REGION" in s["label"] and "year" in s["label"] for s in d["suggested_abstractions"]))

    def test_two_keys_and_edges(self):
        rc, out, _ = run("profile_data.py", os.path.join(FIX, "two_keys.csv"))
        d = json.loads(out)
        self.assertEqual(sorted(d["candidate_keys"]), ["channel", "product"])
        rc, out, _ = run("profile_data.py", os.path.join(FIX, "edges.csv"))
        d = json.loads(out)
        self.assertIn("weight", d["candidate_values"])


class TestScoringTiers(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(scoring.tier(0.85), "REUSE")
        self.assertEqual(scoring.tier(0.6), "ADAPT")
        self.assertEqual(scoring.tier(0.3), "NONE")


if __name__ == "__main__":
    unittest.main()
