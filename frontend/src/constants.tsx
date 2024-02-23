export const RESULT_COUNT_LIST = [5, 10, 15] as const;
export type ResultCount = typeof RESULT_COUNT_LIST[number];

export enum SortOption {
  Date = "Date",
  Similarity = "Similarity",
}

export const SORT_OPTIONS_LIST: SortOption[] = Object.values(SortOption) as SortOption[];
