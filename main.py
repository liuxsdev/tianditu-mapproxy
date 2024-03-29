from pathlib import Path

import yaml

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/102.0.5005.167 Safari/537.36"

headers = {
    "headers": {
        "Referer": "https://www.tianditu.gov.cn/",
        "User-Agent": USER_AGENT,
    }
}

TianMapInfo = {
    "vec": "天地图-矢量地图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像地图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "eva": "天地图-英文矢量注记",
    "eia": "天地图-英文影像注记",
    "ibo": "天地图-全球境界",
}

config = {
    "services": {
        "demo": {},
        "tms": {"use_grid_names": True, "origin": "nw"},
        "kml": {"use_grid_names": True},
        "wmts": {
            "md": {
                "title": "Tianditu MapProxy WMTS Proxy",
                "abstract": "Tianditu MapProxy WMTS Proxy",
            }
        },
        "wms": {
            "md": {
                "title": "Tianditu MapProxy WMS Proxy",
                "abstract": "Tianditu MapProxy WMS Proxy",
            }
        },
    }
}


def get_tianditu_url(map_type: str, token: str):
    return (
        f"https://t4.tianditu.gov.cn/{map_type}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
        + f"&LAYER={map_type}&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&"
        + f"TileCol=%(x)s&TileRow=%(y)s&TileMatrix=%(z)s&tk={token}"
    )


def new_sources(
    map_type: str, url: str, grid: str, transparent: bool, http: dict = None
):
    r = {"type": map_type, "url": url, "grid": grid, "transparent": transparent}
    if http:
        r["http"] = http
    return r


def generate_config(token: str):
    sources = {}
    caches = {}
    layers = []

    for key, _ in TianMapInfo.items():
        sources_name = f"tianditu_{key}"  # 也作为缓存文件名
        cache_name = f"tianditu_{key}_cache"
        transparent = False
        if key in ["cva", "cia", "cta", "eia", "ibo"]:
            transparent = True
        sources[sources_name] = new_sources(
            "tile",
            get_tianditu_url(key, token),
            "GLOBAL_WEBMERCATOR",
            transparent,
            http=headers,
        )
        caches[cache_name] = {
            "grids": ["GLOBAL_WEBMERCATOR"],
            "sources": ["tianditu_" + key],
            "cache": {
                "type": "geopackage",
                "table_name": key,
                "filename": f"{TianMapInfo[key]}.gpkg",
            },
        }
        layers.append(
            {
                "name": "tianditu_" + key,
                "title": TianMapInfo[key],
                "sources": [cache_name],
                "md": {"abstract": TianMapInfo[key]},
            }
        )

    config["layers"] = layers
    config["sources"] = sources
    config["caches"] = caches
    return config


def generate_yaml(token):
    print(f"使用tk: {token}生成配置文件")
    config_ = generate_config(token)
    y = yaml.dump(
        config_, default_flow_style=False, sort_keys=False, allow_unicode=True
    )
    with open("tianditu_mapproxy.yaml", "w", encoding="utf-8") as f1:
        f1.write(y)
    print("生成配置文件 tianditu_mapproxy.yaml")


if __name__ == "__main__":
    cwd = Path.cwd()
    tk_file_path = cwd.joinpath("tk.txt")
    if tk_file_path.exists():
        with open(tk_file_path, "r", encoding="utf-8") as f:
            tk = f.read()
            generate_yaml(tk)

    else:
        with open(tk_file_path, "w", encoding="utf-8") as f:
            tk = input("请输入天地图token:")
            f.write(tk)
            generate_yaml(tk)
