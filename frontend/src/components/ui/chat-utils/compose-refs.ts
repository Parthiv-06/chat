// Merges several refs (callback or object) into one callback ref for a single element.
// The returned callback is memoised on the refs, so pass stable refs to avoid re-attaching.
import * as React from "react"

type PossibleRef<T> = React.Ref<T> | undefined

function setRef<T>(ref: PossibleRef<T>, value: T | null) {
  if (typeof ref === "function") ref(value)
  else if (ref) (ref as React.RefObject<T | null>).current = value
}

export function useComposedRefs<T>(...refs: PossibleRef<T>[]) {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return React.useCallback((node: T | null) => refs.forEach((r) => setRef(r, node)), refs)
}
