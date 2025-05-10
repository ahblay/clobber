import Mathlib.SetTheory.Game.PGame

open SetTheory
open PGame

set_option trace.Meta.Tactic true

/-- The game Up, defined as {0 | star}. -/
def Up : PGame :=
  ⟨Unit, Unit, fun _ ↦ 0, fun _ ↦ SetTheory.PGame.star⟩

/-- The candidate game {0 | Up + star}. -/
def Up_Up : PGame :=
  ⟨Unit, Unit, fun _ ↦ 0, fun _ ↦ Up + SetTheory.PGame.star⟩

def nCopiesUp : ℕ → PGame
| 0     => 0
| (n+1) => nCopiesUp n + up

def n : Nat := 1
#check nCopiesUp n

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h with
  | inr hq => apply Or.inl; exact hq
  | inl hp => apply Or.inr; exact hp

theorem n_mul_up_eq (n : ℕ)
    : nCopiesUp (n + 1) = PGame.mk PUnit PUnit (λ _ => 0) (λ _ => nCopiesUp n + star) := by
  induction n
  apply PGame.ext
  simp [nCopiesUp]
  rfl

theorem sum_up_eq_up_up (hu huu : PGame) (hu : Up) (huu : Up_Up) : huu := by
  apply PGame.ext
  exact
