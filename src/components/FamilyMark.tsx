import { FAMILIES, familyVar, type FamilyId } from "../families";

/** A dot in the family's colour, optionally with its name. */
export default function FamilyMark({
  family,
  label = false,
}: {
  family: FamilyId;
  label?: boolean;
}) {
  return (
    <span className="family-mark" style={{ color: familyVar(family) }}>
      <span className="family-dot" aria-hidden="true" />
      {label ? (
        <span className="family-label">{FAMILIES[family].label}</span>
      ) : (
        <span className="sr-only">{FAMILIES[family].label}</span>
      )}
    </span>
  );
}
