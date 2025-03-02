Shader "Custom/UnlitGrid"
{
    Properties
    {
        _Color1 ("Color 1", Color) = (1,1,1,1)
        _Color2 ("Color 2", Color) = (0,0,0,1)
        _GridScale ("Grid Scale", Float) = 1
    }
    SubShader
    {
        Tags {
            "RenderType"="Opaque"
            "Queue"="Geometry"
        }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_shadowcaster

            #include "UnityCG.cginc"
            
            struct appdata_t
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float3 world_pos : TEXCOORD0;
            };

            float4 _Color1;
            float4 _Color2;
            float _GridScale;
            
            v2f vert (appdata_t v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.world_pos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                float2 grid_uv = (i.world_pos.xz / _GridScale) + float2(0.5, 0.5);
                bool even_x = floor(grid_uv.x) % 2 == 0;
                bool even_y = floor(grid_uv.y) % 2 == 0;

                return even_x ^ even_y ? _Color1 : _Color2;
            }

            ENDCG
        }
    }
}
