package com.oneonone.algorithms;

import java.util.*;

/** Random-pivot, three-way partitioning; caller's array is not modified. */
public final class Quickselect {

  public int select(int[] source, int k, long seed) {
    if (
      source == null || source.length == 0 || k < 0 || k >= source.length
    ) throw new IllegalArgumentException(
      "A nonempty dataset and valid zero-based position are required"
    );
    int[] a = source.clone();
    Random r = new Random(seed);
    int lo = 0,
      hi = a.length - 1;
    while (lo < hi) {
      int pivot = a[lo + r.nextInt(hi - lo + 1)],
        lt = lo,
        i = lo,
        gt = hi;
      while (i <= gt) {
        if (a[i] < pivot) swap(a, lt++, i++);
        else if (a[i] > pivot) swap(a, i, gt--);
        else i++;
      }
      if (k < lt) hi = lt - 1;
      else if (k > gt) lo = gt + 1;
      else return a[k];
    }
    return a[lo];
  }

  private void swap(int[] a, int i, int j) {
    int t = a[i];
    a[i] = a[j];
    a[j] = t;
  }

  public Map<String, Integer> quartiles(int[] a, long seed) {
    return Map.of(
      "q1",
      select(a, Math.max(0, (int) Math.ceil(a.length * .25) - 1), seed),
      "median",
      select(a, Math.max(0, (int) Math.ceil(a.length * .5) - 1), seed + 1),
      "q3",
      select(a, Math.max(0, (int) Math.ceil(a.length * .75) - 1), seed + 2)
    );
  }
}
