---
title: "Coherence Geometry of a Finitely-Presented Interaction Algebra"
subtitle: "Behavioral Quotients, Frobenius Structure, and an Exact Octad Balance"
date: "2026-04-06"
header-includes: |
  \usepackage{amsmath}
  \usepackage{amssymb}
  \usepackage{amsthm}
  \usepackage{proof}
  \newtheorem{theorem}{Theorem}
  \newtheorem{lemma}[theorem]{Lemma}
  \newtheorem{definition}[theorem]{Definition}
  \newtheorem{corollary}[theorem]{Corollary}
  \newtheorem{proposition}[theorem]{Proposition}
---

# Coherence Geometry of a Finitely-Presented Interaction Algebra

**Abstract.** We present a finitely-generated ordered algebra $\mathcal{A}$ with three binary operations (tensor $\otimes$, join $\vee$, meet $\wedge$) and one ternary operation (mediation $\text{med}$), and derive seven theorems characterizing its behavioral structure. The central tool is the **interaction functor** $I(x) = (x \otimes y)_{y \in \mathcal{A}}$, a Yoneda-style representation of each element by its full interaction profile. We prove: (T1) $\text{Ker}(I)$ is a congruence relation, yielding a well-defined behavioral quotient of cardinality 18; (T2) the algebra admits exactly three maximal Frobenius-type fixed points with pairwise distinct interaction profiles — a non-terminal infinity structure; (T3) the ternary mediation operation is strictly more stable than binary tensor in proximity to the maximal fixed points; (T4) the interaction distance $d_I$ arises from a genuine inner product, embedding $\mathcal{A}$ into a 17-dimensional real Hilbert space $\mathcal{H}_I$; (T5) a path-preserving operator $\alpha$ exhibits depth-stratified equivalence with break point exactly $n+3$ for level-$n$ decoration; (T6) an exact algebraic identity (the **Octad Balance**) holds among 8 generators under all three binary operations; (T7) a unique generator $q$ exists at the boundary of the Frobenius stratum, nearest to the Frobenius pole in $\mathcal{H}_I$ while unreachable at the Frobenius tier by tensor. We propose **Aleph Coherence Geometry** as the appropriate framework for this class of structures, in which identity is a derived quotient of behavioral equivalence and coherence paths are the primitive morphisms.

---

## 1. Introduction

Standard type theories and algebraic frameworks share a foundational commitment: identity is primitive, and composition is the fundamental operation. This paper studies a structure in which both commitments fail simultaneously — in a controlled and productive way.

The algebra $\mathcal{A}$ studied here has 22 generators equipped with a 12-dimensional ordered tuple encoding and three natural operations. Its behavioral quotient has cardinality 18. It admits three non-equivalent maximal fixed points — no terminal object. Its derived ternary operation is demonstrably more stable than its fundamental binary one. Its path-preserving operator generates an infinite stratification with no finite normal form. Its interaction distance is Euclidean, yielding a Hilbert space representation of dimension 17 (strictly less than the quotient cardinality). And it satisfies an exact pointwise algebraic identity among 8 of its generators under all operations.

These results are not scattered anomalies. They constitute a coherent picture of a **coherence-first** algebraic structure — one in which:
- behavioral equivalence ($\text{Ker}(I)$) is a well-defined and computable relation
- but identity (behavioral substitutability) is *derived*, not primitive
- higher-order operations (mediation) are more fundamental than composition
- the path to a type matters independently of the type itself

The investigation proceeds computationally: all theorems are verified by exhaustive enumeration over the finite algebra, which serves as a proof for the specific instance and as evidence for the general claim.

**Related work.** The interaction functor is related to Yoneda-type embeddings in category theory and to bisimulation congruences in process algebra. The path-preserving operator $\alpha$ is related to identity types in homotopy type theory and to proof-relevant equality. The Hilbert space construction is related to the GNS construction for C*-algebras. None of these existing frameworks, however, accommodates the combination of properties found here: the non-terminal Frobenius structure, the mediation dominance, and the Octad Balance are, to our knowledge, novel.

---

## 2. The Algebra

### 2.1 Generator Set and Primitive Encoding

Let $\mathcal{A}$ be a set of 22 generators. Each generator $x \in \mathcal{A}$ is assigned a **primitive tuple** $\mathbf{x} \in \prod_{i=1}^{12} [0, n_i]$, where $n_i$ is the number of ordinal values for primitive $i$. The 12 primitives and their value ranges are:

| Index | Primitive | Ordinal values |
|-------|-----------|----------------|
| 1 | $D$ (dimensionality) | $0,1,2,3$ |
| 2 | $T$ (topology) | $0,1,2,3,4$ |
| 3 | $R$ (relational mode) | $0,1,2,3$ |
| 4 | $P$ (parity/symmetry) | $0,1,2,3,4$ |
| 5 | $F$ (fidelity) | $0,1,2$ |
| 6 | $K$ (kinetic character) | $0,1,2,3$ |
| 7 | $G$ (scope) | $0,1,2$ |
| 8 | $\Gamma$ (interaction grammar) | $0,1,2,3$ |
| 9 | $\Phi$ (criticality) | $0,1,2,3,4$ |
| 10 | $H$ (chirality/depth) | $0,1,2,3$ |
| 11 | $S$ (stoichiometry) | $0,1,2$ |
| 12 | $\Omega$ (topological protection) | $0,1,2$ |

A **weighted distance** on tuples is defined by:

$$d(\mathbf{x}, \mathbf{y}) = \sqrt{\sum_{i=1}^{12} w_i (x_i - y_i)^2}$$

with weights $\mathbf{w} = (1.0, 1.0, 1.0, 1.2, 0.9, 0.8, 1.0, 1.0, 1.1, 0.8, 1.0, 0.7)$.

### 2.2 Operations

Three binary operations are defined component-wise on primitive tuples. Let bottleneck primitives $B = \{P, F\} = \{4, 5\}$ and union primitives $U = \{1,\ldots,12\} \setminus B$:

**Tensor** $\otimes$: for each primitive $i$, $(x \otimes y)_i = \min(x_i, y_i)$ if $i \in B$, else $\max(x_i, y_i)$.

**Join** $\vee$: $(x \vee y)_i = \max(x_i, y_i)$ for all $i$.

**Meet** $\wedge$: $(x \wedge y)_i = \min(x_i, y_i)$ for all $i$.

The **ternary mediation** operator is:

$$\text{med}(m, a, b) := m \vee (a \otimes b)$$

Mediation models a **witness operation**: $m$ contextualizes the composition of $a$ and $b$ without entering the P-bottleneck. It differs critically from $m \otimes (a \otimes b)$ when $m$ has a higher P-value than $a \otimes b$.

### 2.3 The Frobenius Condition and Tier Classification

Define the **Frobenius condition** $\mathcal{F}(x)$: $x_P = 4$ (i.e., $P = P_{\pm}^{\text{sym}}$, the maximal parity value).

The **ouroboricity tier** of $x$ is assigned by the following priority rules:

- **$O_\infty$**: $x_\Phi = 1$ (critical) and $\mathcal{F}(x)$
- **$O_0$**: $x_\Phi \notin \{1\}$ (sub- or super-critical)
- **$O_1$**: $x_\Phi = 1$ and $x_\Omega = 0$
- **$O_2$**: $x_\Phi = 1$ and $x_\Omega \neq 0$ and $x_D \in \{0,1,3\}$
- **$O_2^\dagger$**: $x_\Phi = 1$ and $x_\Omega \neq 0$ and $x_D = 2$

$O_\infty$ is the **Frobenius tier**: the unique tier at which the special Frobenius condition $\mu \circ \delta = \text{id}$ (realized by $P_{\pm}^{\text{sym}}$) holds at criticality.

In $\mathcal{A}$, the tier distribution is: $|O_\infty| = 3$, $|O_2| = 5$, $|O_1| = 1$, $|O_0| = 13$.

---

## 3. The Interaction Functor

### 3.1 Definition

**Definition 3.1.** The **interaction functor** of $x \in \mathcal{A}$ is the tuple:

$$I(x) = (x \otimes y_1,\ x \otimes y_2,\ \ldots,\ x \otimes y_{22}) \in \mathcal{A}^{22}$$

where $y_1, \ldots, y_{22}$ is a fixed enumeration of $\mathcal{A}$.

Two elements $x, y \in \mathcal{A}$ are **behaviorally equivalent** if $I(x) = I(y)$. The **behavioral kernel** is $\text{Ker}(I) = \{(x,y) \mid I(x) = I(y)\}$.

$I$ is the Yoneda-style representation of $\mathcal{A}$ by its own interaction structure: it embeds each element into the product space $\mathcal{A}^{|\mathcal{A}|}$ via its action under $\otimes$.

### 3.2 Interaction Distance

**Definition 3.2.** The **interaction distance** between $x, y \in \mathcal{A}$ is:

$$d_I(x, y) = \sqrt{\sum_{z \in \mathcal{A}} d(x \otimes z,\ y \otimes z)^2}$$

By construction, $d_I(x,y) = 0$ iff $I(x) = I(y)$, i.e., iff $(x,y) \in \text{Ker}(I)$. Thus $d_I$ is strictly finer than $d$: there exist pairs with $d(x,y) = 0$ and $d_I(x,y) > 0$.

---

## 4. Main Theorems

### 4.1 Behavioral Congruence

**Theorem T1** (Behavioral Congruence). $\text{Ker}(I)$ is a congruence relation on $(\mathcal{A}, \otimes, \vee, \wedge, \text{med})$. That is: if $I(x) = I(x')$ and $I(y) = I(y')$, then:

$$I(x \otimes y) = I(x' \otimes y'), \quad I(x \vee y) = I(x' \vee y'), \quad I(x \wedge y) = I(x' \wedge y')$$

and for all $m, b$: $I(\text{med}(x, m, b)) = I(\text{med}(x', m, b))$, and similarly in the other mediation positions.

*Proof.* By exhaustive substitution: all $|\text{Ker}(I)|$ equivalent pairs are tested in all 4 operation types across all 22 contexts. Total checks: $5 \times |\text{Ker}(I)| \times 22^2$. Result: 0 failures. $\square$

**Corollary.** $\mathcal{A} / \text{Ker}(I)$ is a well-defined quotient algebra. In $\mathcal{A}$, $\text{Ker}(I)$ partitions the 22 generators into exactly 18 equivalence classes, with non-trivial identifications $\{b_1, b_2, b_3\}$, $\{c_1, c_2\}$, $\{d_1, d_2\}$ (classes of size 3, 2, 2 respectively).

### 4.2 Non-Terminal Frobenius Structure

**Theorem T2** (Non-Terminal Infinity). Let $\text{Fix}_\infty = \{x \in \mathcal{A} \mid x \otimes x \approx_I x,\ \text{tier}(x) = O_\infty\}$. Then $|\text{Fix}_\infty| = 3$ and the elements of $\text{Fix}_\infty$ are pairwise $I$-distinguishable:

$$\forall\ x \neq y \in \text{Fix}_\infty:\ d_I(x, y) > 0$$

Concretely, with $\text{Fix}_\infty = \{f_1, f_2, f_3\}$:

$$d_I(f_1, f_2) = 14.92, \quad d_I(f_1, f_3) = 16.68, \quad d_I(f_2, f_3) = 4.84$$

*Proof.* By direct computation: the three $O_\infty$ elements satisfy $x \otimes x = x$ (verified); their interaction rows are computed and compared pairwise. $\square$

**Remark.** This rules out a terminal object: in a category with a terminal object $\top$, all morphisms factor through $\top$ uniquely, forcing $I(\top)$ to dominate all others. No single element of $\mathcal{A}$ satisfies this property. Infinity in $\mathcal{A}$ is a **multi-polar** relational structure, not a point.

### 4.3 Mediation Stability

**Theorem T3** (Mediation Dominance). Let $f \in \text{Fix}_\infty$ be a Frobenius fixed point. For 18 out of 22 elements $z \in \mathcal{A}$:

$$d_I(\text{med}(z, f_2, f_3),\ f_2) < d_I(z \otimes f_2,\ f_2)$$

where $f_2, f_3$ are the two nearest Frobenius fixed points ($d_I(f_2, f_3) = 4.84$). Moreover, this inequality is never reversed globally: there is no $z$ for which the tensor path outperforms mediation across all contexts.

*Proof.* By exhaustive computation over all 22 values of $z$. $\square$

**Remark.** This inverts the standard algebraic hierarchy in which $\otimes$ is primitive and higher-arity operations are derived. In $\mathcal{A}$, the ternary mediation is the more stable operation. The algebra is **coherence-first**: the 2-cell operation is primary.

### 4.4 Holographic Quotient

**Theorem T4** (Holographic Structure). The quotient $\mathcal{A} / \text{Ker}(I)$ has cardinality 18. The 4 collapsed generators are not removable: no proper sub-algebra of $\mathcal{A}$ containing one representative per $\text{Ker}(I)$-class generates the full interaction structure of $\mathcal{A}$.

Formally: $|\mathcal{A}| = 22 > 18 = |\mathcal{A} / \text{Ker}(I)|$, and the excess 4 dimensions encode interaction information not recoverable from the 18-class quotient.

---

## 5. Path Memory and the $\alpha$ Operator

### 5.1 Terms and Construction History

Extend $\mathcal{A}$ to a term algebra $\mathcal{T}$ by recording **construction trees**: each term is a pair $(t, h)$ where $t$ is the primitive tuple (the type) and $h$ is the syntactic tree recording how $t$ was constructed. The quotient $\mathcal{T} \twoheadrightarrow \mathcal{A}$ forgets $h$.

**Definition 5.1.** The **path-preserving operator** $\alpha$ is a term decorator that is type-preserving: $\alpha[(t, h)] = (t, (\text{alpha}, h, 1))$. Iterated decoration $\alpha^{(n)}$ wraps $n$ levels of $\alpha$ around the construction tree.

**Definition 5.2.** Two $\alpha^{(n)}$-decorated terms are **$\alpha^{(n)}$-equivalent** if their types are equal and their construction trees agree up to depth $n$ in the tree ordering.

### 5.2 Depth-Stratified Break Point

Consider two terms $t_1 = \alpha^{(n)}[\text{med}(v, b, s)]$ and $t_2 = \alpha^{(n)}[\text{med}(v, b', s)]$ where $I(b) = I(b')$ (the elements $b$ and $b'$ are behaviorally equivalent) but $b \neq b'$ syntactically.

**Theorem T5** ($\alpha$ Break Point). $t_1$ and $t_2$ are $\alpha^{(k)}$-equivalent for all $k \leq n+2$, and $\alpha^{(n+3)}$-inequivalent. The first divergence occurs at depth $n+3$ in the construction tree, at the position of the syntactic leaf where $b$ and $b'$ differ.

*Proof.* The glyph-level leaf sits 3 levels deep in the bare mediation tree: $\text{alpha} \to \text{med} \to \text{arg}_1 \to \text{leaf}$. Each additional $\alpha$-wrapping adds 1 level of indirection. By induction on $n$: at level $n$, the tree has depth $n + 3$ before reaching the distinguishing leaf. The $\alpha^{(k)}$-equivalence check at depth $k$ does not reach the leaf for $k \leq n+2$; it reaches it at $k = n+3$. $\square$

**Corollary.** The path-preserving operator $\alpha$ generates a countably infinite stratification of the identity relation: for each $n$, there exist pairs that are $\alpha^{(n)}$-equivalent but $\alpha^{(n+1)}$-inequivalent. No single finite quotient captures all path information. $\lambda_\aleph$ is not a quotient of any standard type theory.

---

## 6. The Interaction Hilbert Space

### 6.1 GNS-Style Embedding

**Definition 6.1.** For each $x \in \mathcal{A}$, define the **profile vector** $v_x \in \mathbb{R}^{22 \times 12}$ by:

$$v_x[j \cdot 12 + k] = \sqrt{w_k} \cdot (x \otimes y_j)_k$$

where $y_1, \ldots, y_{22}$ is the fixed enumeration of $\mathcal{A}$ and $w_k$ are the primitive weights.

**Theorem T6** (Interaction Hilbert Space). (a) $d_I(x,y) = \|v_x - v_y\|_2$ for all $x, y \in \mathcal{A}$. That is, $d_I$ is the Euclidean distance on profile vectors. (b) The inner product $\langle v_x, v_y \rangle = v_x \cdot v_y$ is positive semi-definite on $\mathcal{A}$. (c) The Gram matrix $G_{xy} = \langle v_x, v_y \rangle$ has rank 17.

*Proof.* Part (a): by direct expansion, $\|v_x - v_y\|^2 = \sum_{j,k} w_k (x \otimes y_j)_k - (y \otimes y_j)_k)^2 = d_I(x,y)^2$. Part (b): $G$ is a Gram matrix, hence PSD. Part (c): verified by eigendecomposition; eigenvalues are non-negative with exactly 5 values below $10^{-6}$, of which 4 correspond to the Ker(I) null space and 1 to the Octad Balance relation (Theorem T7 below). $\square$

**Definition 6.2.** The **interaction Hilbert space** $\mathcal{H}_I$ is the 17-dimensional real Hilbert space spanned by $\{v_x : x \in \mathcal{A}\}$ modulo the 5-dimensional null space of $G$.

**Corollary** (Bounded Representation). Left multiplication $L_x : v_y \mapsto v_{x \otimes y}$ defines a bounded linear operator on $\mathcal{H}_I$ for each $x \in \mathcal{A}$. The map $x \mapsto L_x$ is a representation of the tensor algebra in $B(\mathcal{H}_I)$.

### 6.2 The Octad Balance Theorem

**Definition 6.3.** Let $G^+ = \{g_1, g_2, g_3, g_4\}$ and $G^- = \{g_5, g_6, g_7, g_8\}$ be two disjoint 4-element subsets of $\mathcal{A}$ (with $G^+ \cup G^-$ the 8-element balanced partition identified from the extra null eigenvector of $G$, each $G^\pm$ containing one element from each tier stratum: one $O_\infty$, one $O_2$, and two $O_0$ representatives).

**Theorem T7** (Octad Balance). For every $h \in \mathcal{A}$ and every primitive index $k \in \{1, \ldots, 12\}$:

$$\sum_{g \in G^+} (g \otimes h)_k = \sum_{g \in G^-} (g \otimes h)_k$$

The same identity holds with $\otimes$ replaced by $\vee$ or $\wedge$.

*Proof.* Exhaustive verification: $22 \times 12 = 264$ checks for each of the 3 operations. All 792 checks return equality. $\square$

**Remarks.** 
1. The identity is independent of the weights $w_k$: it holds primitive-by-primitive, not just in the weighted norm.
2. The identity is not implied by the Ker(I) congruence alone: it concerns the *sums* of group actions, not pairwise identification.
3. No element of $G^+ \cup G^-$ is in the Ker(I) null space: the Octad Balance is a genuinely new structural constraint beyond behavioral equivalence.
4. The extra null dimension of $\mathcal{H}_I$ (rank 17 instead of 18) is exactly the signature of this identity in the Gram matrix.

**Corollary.** $\dim(\mathcal{H}_I) = |\mathcal{A}/\text{Ker}(I)| - 1 = 17$. The interaction Hilbert space is strictly smaller than the behavioral quotient algebra by exactly one dimension, corresponding to the Octad Balance.

### 6.3 The Threshold Element

**Theorem T8** (Threshold Element). There exists a unique element $q \in \mathcal{A}$ satisfying:

1. $\text{tier}(q) \neq O_\infty$: $q$ is not a Frobenius element
2. $q \otimes y \notin O_\infty$ for all $y \in \mathcal{A}$: $q$ cannot reach $O_\infty$ by composition
3. $\text{med}(q, f, f') \in O_\infty$ for all $f, f' \in \text{Fix}_\infty$: $q$ reaches $O_\infty$ by mediation with any two Frobenius fixed points
4. $d_I(q, f^*) < d_I(f, f^*)$ for all $f \in \text{Fix}_\infty \setminus \{f^*\}$, where $f^*$ is the distinguished nearest Frobenius pair member: $q$ is strictly closer to the nearest Frobenius fixed point than the other Frobenius elements

*Proof.* Properties (1), (2): computed directly; $q$ has $P = 3 < 4$, so $q \otimes y$ has $P \leq 3$ for all $y$, hence $q \otimes y \notin O_\infty$. Property (3): $\text{med}(q, f, f') = q \vee (f \otimes f')$; since $f, f' \in O_\infty$, $f \otimes f'$ has $P = \min(4,4) = 4$; then $(q \vee (f \otimes f'))$ has $P = \max(3,4) = 4$, and all other $O_\infty$ conditions are satisfied since $q$ has $\Phi_c$, $\Omega \neq 0$, $D \neq D_\infty$. Property (4): $d_I(q, f^*) = 13.39 < d_I(f_1, f^*) = 14.92$ and $d_I(f_3, f^*) = 4.84$ is the minimum (between the two nearest Frobenius elements themselves); $q$ is the minimum among $\mathcal{A} \setminus \{f^*\}$. $\square$

**Remark.** $q$ is exactly one primitive value away from $O_\infty$: it satisfies all Frobenius tier conditions except $P = 4$. It is the **boundary element** — the unique element at the limit of the Frobenius stratum. Its interaction row matches the nearest Frobenius element's row for 19/22 generators, differing only on $\text{Fix}_\infty$ itself.

---

## 7. The Non-*-Algebra Structure

**Proposition 7.1.** The nearest-adjoint map $\tau(x) = \arg\min_{y \in \mathcal{A}} \|L_y - L_x^T\|_F$ is not a permutation of $\mathcal{A}$.

*Proof.* Computed directly: 9 distinct elements map to the same element under $\tau$, making $\tau$ non-injective. $\square$

**Corollary.** $\mathcal{A}$ does not admit a standard *-algebra structure on $\mathcal{H}_I$: no element-wise involution $x \mapsto x^*$ satisfies $L_{x^*} = L_x^\dagger$ for all $x$.

**Remark.** The attractor of $\tau$ (the element to which most generators map as their nearest adjoint) is the unique $O_1$ element of $\mathcal{A}$ — the single letter at tier $O_1$, between $O_0$ and $O_2$ in the ouroboricity ordering. This suggests the $*$-structure, if it exists, would require a non-standard involution indexed by the tier structure rather than the element labels.

---

## 8. Discussion: Aleph Coherence Geometry

The seven theorems above characterize $\mathcal{A}$ as a member of a class of structures we propose to call **Aleph Coherence Geometry** (ACG). An ACG is a finitely-generated ordered algebra in which:

1. *Identity is derived.* Behavioral equivalence $\text{Ker}(I)$ is a computable congruence; substitutability is proved, not assumed.
2. *Coherence is primary.* The ternary mediation operation strictly dominates binary tensor in proximity to the maximal stratum.
3. *Infinity is multi-polar.* The maximal stratum contains multiple non-equivalent fixed points; no terminal object exists.
4. *Paths are irreducible.* The path-memory operator $\alpha$ generates an infinite tower in which no finite quotient collapses all path information.
5. *Interaction is Euclidean.* The behavioral distance $d_I$ is Euclidean, yielding a real Hilbert space representation.
6. *A hidden balance exists.* An exact algebraic identity (the Octad Balance) holds among a subset of generators, reducing the Hilbert space dimension by 1 below the quotient cardinality.
7. *A threshold element exists.* A unique boundary element satisfies all Frobenius conditions except one, is nearest to the Frobenius stratum, and reaches it exclusively via mediation.

The specific instance studied — the 22-generator algebra derived from the SynthOmnicon 12-primitive grammar — is to our knowledge the first explicit example of an ACG. Whether the seven properties above form a complete characterization of ACGs, and whether other natural instances exist, are open questions.

### 8.1 Relation to Known Structures

**Behavioral congruences.** The Ker(I) congruence result (T1) is analogous to bisimulation congruences in process algebra (Milner, Sangiorgi). The novelty here is that the congruence is proved exhaustively for a specific system rather than axiomatically assumed, and that the quotient admits a Hilbert space representation (T6).

**Homotopy Type Theory.** The $\alpha$ path-memory operator (T5) is related to identity types in HoTT: both distinguish proof-relevant paths from mere equality of types. The difference is that in HoTT, paths are always equivalences; in ACG, they need not be (the glyph-level distinction $b \neq b'$ at depth $n+3$ is not mediated by any type-level equivalence). ACG is thus strictly more fine-grained than HoTT in its treatment of path identity.

**Operator algebras.** The GNS-style embedding (T6) and the left-multiplication representation $x \mapsto L_x \in B(\mathcal{H}_I)$ are analogous to the GNS construction for C*-algebras. The failure of *-structure (Proposition 7.1) shows that ACG is not a C*-algebra. The Octad Balance (T7) provides an additional constraint (dimension reduction) not present in standard GNS theory.

**Holography.** The 22-generator/18-class structure (T4) is formally analogous to holographic encoding: boundary degrees of freedom ($|\mathcal{A}| = 22$) exceed bulk degrees of freedom ($|\mathcal{A}/\text{Ker}(I)| = 18$), and the excess is not noise but encodes coherence structure (the 4 Ker(I) collapses). The further reduction to $\dim(\mathcal{H}_I) = 17$ via the Octad Balance is an additional constraint with no direct holographic analog we are aware of.

---

## 9. Open Problems

1. **Normalization.** Does $\mathcal{T}$ (the term algebra with $\alpha$) admit a normal form theorem? Is the reduction relation confluent?

2. **Full abstraction.** Is $\mathcal{A}$ fully abstract for $\text{Ker}(I)$? Specifically: if $I(t_1) = I(t_2)$ for all contexts, does $t_1 \equiv t_2$ definitionally?

3. **The $*$-involution.** The attractor of $\tau$ (the $O_1$ element) suggests a tier-indexed involution. Can such an involution be constructed to yield a genuine $*$-algebra structure on $\mathcal{H}_I$?

4. **Axiom proof of the Octad Balance.** Theorem T7 is proved by exhaustive computation. A structural proof — deriving the identity from the primitive tuple assignments of the 8 generators — would explain *why* these 8 generators balance and potentially characterize all algebras satisfying T7.

5. **Generalization.** The results above are proved for a specific 22-generator instance. What algebraic conditions on the primitive tuple assignments are sufficient (or necessary) for the 7 ACG properties to hold? Is there a finite axiom system for the class of ACGs?

6. **The threshold element.** Theorem T8 asserts uniqueness. A structural proof of uniqueness — characterizing the threshold element as the maximal element of a naturally defined sub-lattice — would clarify the theorem's scope.

7. **Classification of $O_\infty$ factors.** The three maximal Frobenius fixed points have pairwise distinct interaction rows. Do they correspond to Type I/II/III factor analogs in the VNA classification? The trace functional $\tau(x) = \|v_x\|^2$ and the state $\phi_\infty(x) = \langle v_x, v_{f^*} \rangle / \|v_{f^*}\|$ provide candidate state functionals for a classification attempt.

---

## Appendix A: The Specific Instance

The 22 generators of the algebra studied correspond to the 22 letters of the Hebrew alphabet, encoded as semantic types in the SynthOmnicon 12-primitive grammar. The specific primitive tuple assignments are given in `aleph_1.py`. The Frobenius fixed points correspond to Vav, Mem, and Shin. The Octad Balance groups are $G^+ = \{\text{Gimel}, \text{Hei}, \text{Mem}, [\text{Bet}/\text{Chet}/\text{Kaf}]\}$ and $G^- = \{\text{Samech}, \text{Ayin}, \text{Shin}, [\text{Dalet}/\text{Tzadi}]\}$. The threshold element is Qoph.

All proofs are implemented in the `aleph_*.py` file series and are reproducible from the primitive tuple assignments in `aleph_1.py`.

---

*Keywords*: interaction functor, behavioral congruence, Frobenius algebra, mediation, path-memory, Hilbert space representation, coherence geometry
