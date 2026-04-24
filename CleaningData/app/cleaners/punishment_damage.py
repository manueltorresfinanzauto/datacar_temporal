import json

from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate

from tqdm import tqdm

from CleaningData.app.cleaners import LLM

class VehicleDamage():

    def __init__(self):
        pass
    """
    A class used to calculate the damage level of a vehicle and apply a discount based on that level.

    Attributes:
    ----------
    None

    Methods:
    -------
    level_extraction_llm(text: str, user_query: str = " ", ai_queries: str = " ") -> json:
        Extracts the damage level from a given text using a language model.
    calculate_percentage(level: int) -> float:
        Calculates the discount percentage based on the damage level.
    calculate_price(price: float, percentage: float) -> float:
        Calculates the final price after applying the discount.
    level(json_level: json) -> int:
        Extracts the damage level from a JSON response.
    return_price(price: float, text: str) -> float:
        Calculates the final price after extracting the damage level and applying the discount.
    """

    def level_extraction_llm(self, text: str, user_query: str = " ",
                             ai_queries: str = " ") -> json:
        """
        Extracts the damage level from a given text using a language model.

        Parameters:
        ----------
        text : str
            The text describing the damage.
        user_query : str, optional
            The user's query (default is " ").
        ai_queries : str, optional
            The AI's previous queries (default is " ").

        Returns:
        -------
        json
            A JSON response containing the damage level.
        """
        template = """
            You are an assistant responsible for classifying vehicle damage based on its severity.
            Previous analysis memory: {ai_queries}
            Damage description: {text}

            Expected classification:  
            - "level" (integer: 1, 2, 3, 4, 5) based on severity.          
            - Returns `None` if there is not enough information.  

            Criteria:  
            
            1. **Level 1 (Minor damage)**:  
                Description:

                - Cosmetic or minor mechanical damage that does not affect the vehicle’s performance or safety.
                - Includes superficial scratches, dents, and minor part replacements.
                - No impact on the structural integrity of the vehicle.
                - Investment: Less than 1,500,000 COP.

                Examples:

                a. Scratches & Paint Damage:
                    - Light scratches on the passenger door due to contact with a bush. (500,000 COP)
                    - Paint chipping on the rear bumper from parking mishap. (1,200,000 COP)
                b. Minor Dents & Bodywork Issues:
                    - Small dent on the trunk lid from a shopping cart. (1,000,000 COP)
                    - Rear door slightly bent but fully functional. (1,400,000 COP)
                c. Component Replacements:
                    - Side mirror cracked, needs replacement. (1,200,000 COP)
                    - Windshield wiper mechanism failing, requires a new motor." (900,000 COP)
                d. Tire & Wheel Damage:
                    - One tire needs replacement due to puncture. (1,100,000 COP)
                    - Slight curb rash on alloy rims, cosmetic issue only. (800,000 COP) 


        
            2. **Level 2 (Moderate damage)**:  
                Description:
                - Damage affecting important but non-critical systems, such as braking, electrical, or suspension.
                - Repairs are required to restore full functionality but the car is still drivable.
                - Investment: Between 1,500,000 - 3,000,000 COP.
                - Mild oxidation focus (small areas of rust that do not compromise structural integrity).
                - Red soil presence, which can indicate prolonged exposure to harsh environmental conditions.

                Examples:

                a. Braking System Issues:
                    - Brake pads and discs worn out, need replacement. (2,000,000 COP)
                    - Handbrake cable snapped, requires repair. (1,800,000 COP)
                b. Electrical System Malfunctions:
                    - Alternator failure causing battery charging issues. (2,500,000 COP)
                    - Dashboard warning lights due to faulty sensors. (2,300,000 COP)
                c. Moderate Panel Damage:
                    - Front fender dented, needs replacement. (2,800,000 COP)
                    - Side skirt damage after minor collision with curb. (2,400,000 COP)
                d. Suspension Issues:
                    - Shock absorbers worn out, affecting ride comfort. (2,700,000 COP)
                    - Control arm slightly bent, requires alignment. (2,900,000 COP)
                e. Mild oxidation and Red Soil presence:
                    - Surface rust on the undercarriage due to exposure to salinity in coastal areas.
                    - Minor oxidation on door hinges and bolts. (2,000,000 COP)
                    - Red soil accumulation in wheel wells and undercarriage, indicating off-road exposure. (1,800,000 COP)

            
            3. **Level 3 (Severe damage)**:  
                Description:
                - Critical damage affecting major mechanical or structural components, such as the engine, transmission, or drivetrain.
                - Repairs are costly but the vehicle can still be restored.
                - Investment: More than 3,000,000 COP.
                - Considerable oxidation focus, meaning extensive rust affecting important parts like the chassis, suspension, engine, structure, or fuel system.

                Examples:

                a. Issues:
                    - Engine overheating due to a blown head gasket. (4,500,000 COP)
                    - Complete engine replacement required due to internal failure. (5,500,000 COP)
                b. Transmission & Drivetrain Damage:
                    - Clutch completely worn out, needs full replacement. (3,800,000 COP)
                    - Automatic transmission failure, requires rebuild. (6,000,000 COP)
                c. Severe Suspension & Axle Damage:
                    - Rear axle bent after a rear-end collision. (3,700,000 COP)
                    - Steering rack failure causing handling issues. (4,200,000 COP)
                d. Significant Body & Panel Damage:
                    - Hood severely dented, must be replaced. (3,500,000 COP)
                    - Front bumper and grille destroyed after hitting a pole. (3,200,000 COP)
                e. Considerable Oxidation Focus:
                    - Extensive rust on the chassis, weakening its structure. 
                    - Fuel lines corroded due to prolonged oxidation. 
                    - Severe rust in the suspension components, affecting safety.
        
            4. **Level 4 (structural damage mild)**:
                Description:
                - Damage affecting the structural integrity of the car but still repairable.
                - Typically caused by moderate collisions with minor deformation of critical components.
                - May require frame straightening or alignment.

                Examples:

                a. Frame & Body Alignment Issues:
                    - Front bumper misaligned after low-speed frontal impact.
                    - Driver-side door requires force to close properly.
                b. Structural Panel Damage:
                    - Roof dented due to falling debris but still intact.
                    - Trunk lid slightly misaligned after rear impact.
                c. Mild Chassis Deformation:
                    - Door frame slightly bent, but doors still functional.
                    - Underbody panels partially displaced due to speed bump impact.


        
            5. **Level 5 (Unrepairable structural damage)**:
                Description:
                - Severe, irreparable damage compromising the vehicle's chassis and safety.
                - The car is considered a total loss due to catastrophic structural failure.
                
                Examples:

                a. Major Chassis Deformation:
                    - Chassis bent in multiple locations, vehicle is unsalvageable.
                    - Severe impact caused both front and rear frame rails to buckle.
                b. Severe Roof & Floor Damage:
                    - Roof completely collapsed due to rollover accident.
                    - Floor has cracked and collapsed, making repairs impossible.
                c. Frame & Structural Integrity Lost:
                    - Main rails deformed beyond repair after high-speed crash.
                    - Vehicle structure severely displaced, affecting all alignment points.
             
        
            Response format:  
            ```json
        
            {{
                "respuesta": {{
                    "nivel": <nivel>
                }}
            }}
              """

        # Invocation code
        
        try:

            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | LLM | JsonOutputParser()

            ai_query = chain.invoke({
                "user_query": user_query,
                "ai_queries": ai_queries[:1000] if ai_queries else "",
                "text": text[:]
            })
            # return ai_query, ai_query['respuesta']['nivel'] 
            return ai_query['respuesta']['nivel']

        except Exception as e:
            # return {'respuesta': {'nivel': 0}}, 0
            return 0
