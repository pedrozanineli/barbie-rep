🟩: Finished simulation;

🟨: Simulation running;

🟥: Simulation not started.

| Experiment Components | Monomeric Condition | pH | Temperature | Status | Result |
|-----------------------|---------------------|-------------------------|-------------|-------------|-------------------------|
| B1                    | Monomer             | Neutral                 | 300 K       | 🟩    | -                       |
| B1 + 10x PS           | Monomer             | Neutral                 | 300 K       | 🟩    | Box became small (100 Å), needs to be increased |
| SPI                   | Dimer               | Acidic - H addition     | 300 K       | 🟩    | 50 ns simulation, protein closed instead of opening - probably not sufficiently acidic to be at pH=5 |
| SPI                   | Dimer + Spy Tag     | Acidic - protonation    | 300 K       | 🟩    | ~100 ns simulation, the protein did not open |
| SPI                   | Dimer + Spy Tag     | Acidic - without protonation by Charmm (H addition?) | 500 K       | 🟥 | - |
| SPI                   | Dimer + Spy Tag - modified by Chimera | Acidic       | 300 K       | 🟥 | - |
| SPI - metadynamics    | Dimer + Spy Tag     | Acidic                  | 300 K       | 🟥 | - |
