Shader "Custom/LitGridShader"
{
    Properties
    {
        _Color1 ("Color 1", Color) = (1,1,1,1)
        _Color2 ("Color 2", Color) = (0,0,0,1)
        _GridScale ("Grid Scale", Float) = 1
        _Smoothness ("Smoothness", Range(0,1)) = 0
        _Metallic ("Metallic", Range(0,1)) = 0
    }
    SubShader
    {
        Tags {
            "RenderPipeline"="UniversalPipeline"
            "RenderType"="Opaque"
            "Queue"="Geometry"
        }
        LOD 100

        Pass
        {
            Name "ForwardPass"
            Tags
            {
                "LightMode"="UniversalForward"
            }
            
            HLSLPROGRAM
            #define _SPECULAR_COLOR_SPECULAR_COLOR
            #pragma vertex vert
            #pragma fragment frag
            #pragma shader_feature _FORWARD_PLUS
            #pragma shader_feature_fragment _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma shader_feature_fragment _ADDITIONAL_LIGHT_SHADOWS

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial);
            half4 _Color1;
            half4 _Color2;
            float _GridScale;
            half _Smoothness;
            half _Metallic;
            CBUFFER_END;
            
            struct attributes
            {
                float4 position_LS : POSITION;
                float3 normal_LS : NORMAL;
            };

            struct v2f
            {
                float4 position_CS : SV_POSITION;
                float3 position_WS : TEXCOORD0;
                float3 normal_WS : TEXCOORD1;
            };
            
            v2f vert (attributes v)
            {
                v2f o;
                o.position_CS = TransformObjectToHClip(v.position_LS);
                o.normal_WS = TransformObjectToWorldNormal(v.normal_LS);
                o.position_WS = TransformObjectToWorld(v.position_LS);
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                float2 grid_uv = (i.position_WS.xz / _GridScale) + float2(0.5, 0.5);
                bool even_x = floor(grid_uv.x) % 2 == 0;
                bool even_y = floor(grid_uv.y) % 2 == 0;
                bool checkered = even_x ^ even_y;
                float4 c = checkered ? _Color1 : _Color2;

                InputData lighting = (InputData) 0;
                lighting.positionWS = i.position_WS;
                lighting.normalWS = normalize(i.normal_WS);
                lighting.viewDirectionWS = GetWorldSpaceViewDir(i.position_WS);
                lighting.shadowCoord = TransformWorldToShadowCoord(i.position_WS);
                
                SurfaceData surface = (SurfaceData) 0;
                surface.albedo = c;
                surface.alpha = c.w;
                surface.smoothness = _Smoothness;
                surface.metallic = _Metallic;

                return UniversalFragmentBlinnPhong(lighting, surface) + unity_AmbientSky;
            }

            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags
            {
                "LightMode" = "ShadowCaster"
            }
            
            ColorMask 0
            
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"

            float3 _LightDirection;

            struct attributes
            {
                float4 position_LS : POSITION;
                float3 normal_LS : NORMAL;
            };

            struct v2f
            {
                float4 position_CS : SV_POSITION;
            };

            float4 GetShadowPositionHClip(attributes v)
            {
                float3 positionWS = TransformObjectToWorld(v.position_LS);
                float3 normalWS = TransformObjectToWorldNormal(v.position_LS);
                float4 positionCS = TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, _LightDirection));
                positionCS = ApplyShadowClamping(positionCS);
                return positionCS;
            }
            
            v2f vert (attributes v)
            {
                v2f o;
                o.position_CS = GetShadowPositionHClip(v);
                return o;
            }

            half4 frag(v2f i) : SV_Target
            {
                return 0;
            }
            ENDHLSL
        }
    }
}
