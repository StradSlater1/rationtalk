// src/utils.ts

import type { StoryData } from "../assets/data/stories"; // adjust path if needed

/**
 * Given an array of stories and an ordered list of topics,
 * return a new array where stories are interleaved by topic:
 *
 *   TopicA[0], TopicB[0], TopicC[0], TopicA[1], TopicB[1], ...
 *
 * If one topic has fewer stories, it simply skips to the next.
 * Once the interleaved array is built, you can slice(0, count).
 * This version also logs the interleaved result to the console.
 */
export function interleaveByTopic(
  allStories: StoryData[],
  topicOrder: string[]
): StoryData[] {
  // 1) Group stories by topic, in the same order as topicOrder:
  const groups: Record<string, StoryData[]> = {};
  topicOrder.forEach((t) => {
    groups[t] = [];
  });

  // Only keep stories whose topic appears in topicOrder
  allStories.forEach((story) => {
    if (topicOrder.includes(story.topic)) {
      groups[story.topic].push(story);
    }
  });

  // 2) Now “round-robin” each group:
  const result: StoryData[] = [];
  let idx = 0;
  let added: boolean;

  do {
    added = false;
    for (const t of topicOrder) {
      if (groups[t][idx]) {
        result.push(groups[t][idx]!);
        added = true;
      }
    }
    idx++;
  } while (added);

  // 3) Log the final interleaved array to the console:
  console.log("interleaveByTopic → topics:", topicOrder);
  console.log(
    "interleaveByTopic → grouped counts:",
    topicOrder.map((t) => `${t}: ${groups[t].length}`)
  );
  console.log("interleaveByTopic → interleaved result:", result);

  return result;
}
