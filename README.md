# SOP-CN: Sustainability Outlook of Passenger-vehicle for China

## Overview

The Sustainability Outlook of Passenger-vehicle for China (SOP-CN) is an integrated model for examining the transition of China's passenger-vehicle fleet and its implications for energy use, climate emissions, and health-relevant air pollutant emissions. The model simulates annual outcomes from 2021 to 2060 across 31 provincial-level regions in mainland China.

SOP-CN examines how vehicle choices, fleet turnover, travel activity, fuel supply, and electricity generation interact during the transition to lower-emission passenger transport. It distinguishes private-owned and non-private-owned vehicles and represents 24 vehicle alternatives across sedan and SUV/MPV body styles, powertrains, and electric-range categories.

## Research questions

The model is designed to investigate:

- How passenger-vehicle sales and stocks evolve across provinces and vehicle-use groups.
- How electricity-sector decarbonization and ethanol blending affect vehicle choices, energy demand, and well-to-wheel emissions.
- How climate and health-relevant pollutant emissions vary across provinces, vehicle technologies, and sources.
- How differences in vehicle mass and travel needs affect non-exhaust particulate emissions, and how demand-matched battery sizing could reduce these emissions.

## Model structure

SOP-CN links the following components:

1. **Consumer costs and vehicle choice.** A perceived cost of ownership framework combines purchase and operating costs with other choice attributes. A nested-logit model estimates market shares for vehicle alternatives separately for private-owned and non-private-owned markets.
2. **Sales and manufacturer decisions.** A purchase-incidence model estimates provincial passenger-vehicle sales. Manufacturer-financed subsidies are represented through a profit-maximizing optimization process.
3. **Fleet turnover.** An age-structured stock model tracks new sales, vehicle ageing, and retirement across provinces, markets, and vehicle alternatives.
4. **Vehicle activity and energy demand.** Vehicle stocks, travel activity, and energy intensities are combined to estimate liquid-fuel, electricity, and hydrogen demand. Plug-in hybrid operation is divided between electric and fuel modes.
5. **Well-to-wheel emissions.** Energy demand is linked to fuel- and electricity-supply pathways and vehicle operation to estimate climate emissions and emissions of CO, SO₂, NOₓ, VOCs, PM₂.₅, and PM₁₀. Particulate emissions include tyre, brake, and road wear.
6. **Scenario and spatial analysis.** Alternative ethanol-blending and electricity carbon-intensity pathways are compared across provinces and vehicle-use groups. A demand-matched BEV sizing analysis assesses range requirements, battery capacity, curb mass, and potential reductions in non-exhaust particulate emissions.

The well-to-wheel assessment covers energy supply and vehicle operation. It does not represent a complete vehicle life cycle including manufacturing and end-of-life processes, and it does not directly estimate pollutant concentrations, population exposure, or health outcomes.

## Authors and collaborators

SOP-CN was developed by a research team led by **Lanxin Shi**, a doctoral researcher, and **Professor Shiqi (Shawn) Ou** of the **Trans Research Group**, School of Future Technology, South China University of Technology. Model development and the associated research also benefited from the contributions of the study's co-authors and collaborators.

Collaborating institutions and organizations include:

- Guangdong Artificial Intelligence and Digital Economy Laboratory (Guangzhou) (Pazhou Laboratory), China.
- Aramco Research Center, Aramco Americas Company, Detroit, USA.
- China Automotive Data (Tianjin) Co., Ltd., China Automotive Technology and Research Center Co., Ltd., Tianjin, China.
- Technology Strategy and Planning, Saudi Aramco, Dhahran, Saudi Arabia.
- Institute of Climate Change and Sustainable Development, Tsinghua University, Beijing, China.

## Funding and data acknowledgements

This work was funded through the Development Agreement between Saudi Aramco Technologies Company and South China University of Technology (SATC 2024-006).

The authors thank **China Automotive Data (Tianjin) Co., Ltd.** for providing historical passenger-vehicle sales data for the 31 provincial-level regions, as well as other relevant data used in this research. The authors also acknowledge the other data providers and published sources identified in the associated manuscript and supplementary information.

## Reproduction, use, and attribution

Please respect the originality and intellectual contributions of the authors. **Before reproducing the model or its results, please contact the authors** to discuss the appropriate model version, input data, and conditions for data use:

- Lanxin Shi: [lancyshek@gmail.com](mailto:lancyshek@gmail.com)
- Shiqi (Shawn) Ou: [sou@scut.edu.cn](mailto:sou@scut.edu.cn)

Some inputs were supplied by collaborating organizations or obtained from external sources. Their availability and reuse may be subject to the relevant data providers' terms. Please acknowledge the authors, collaborators, and data sources appropriately in any resulting work, and cite the associated paper once its final publication details are available.
