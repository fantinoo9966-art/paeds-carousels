/* The Reel "script" format. One JSON file = one Reel. Written by Claude or by Gemini (agent/reel_script.py).
   Text markup:  *word*   = highlighted word in titles (marker swipe)
                 **word** = key value in body text (red pen for PG, bold for parents) */

export type Mood = "hot" | "sleepy" | "happy" | "think" | "doctor" | "ouch" | "sneeze" | "queasy";

export type Item = { text: string; sub?: string; icon?: string };

export type Scene =
  | { type: "hook"; title: string; sub?: string; mood?: Mood; icon?: string; hand?: string; skin?: string; visual?: "baby" | "xray" }
  | { type: "big"; text: string; sub?: string; visual?: Visual }
  | { type: "split"; title: string; left: Side; right: Side }
  | { type: "list"; title: string; style?: ListStyle; tone?: "good" | "bad" | "alert" | "neutral"; items: Item[] }
  | { type: "cards"; title: string; cards: { title: string; lines: string[] }[] }
  | { type: "pearls"; title: string; items: string[] }
  | { type: "cta"; line?: string; sub?: string };

export type ListStyle = "rows" | "notes" | "chat" | "wheel" | "flags" | "steps" | "chips";

export type Visual =
  | { kind: "calendar"; from: number; to: number; label?: string }
  | { kind: "number"; value: string; label?: string }
  | { kind: "icon"; name: string }
  | { kind: "drop" }
  | { kind: "clock" };

export type Side = { title: string; icon?: string; lines: string[]; verdict?: string };

export type Script = {
  audience: "parents" | "pg";
  topic: string;
  tab?: string; // PG notebook tab, e.g. "PG NOTES · NEONATOLOGY 04"
  disclaimer?: string;
  seed?: number; // varies transitions / entrances / colours
  pace?: number; // 1 = old speed; default 1.3 (slower, user asked 2026-11-17)
  scenes: Scene[];
};
